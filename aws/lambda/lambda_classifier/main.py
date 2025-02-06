# lambda_classifier/main.py
import os
import json
import logging
# import openai
import traceback
from openai import OpenAI
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from database import SessionLocal
from models import BulletinRaw, BulletinProcessed  # or whichever models you use

# from geoloc import GeoCoder
from geoloc_v2 import TwoFileGeoCoder as GeoCoder

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Set your OpenAI API key via environment variable, e.g. in Lambda's configuration
OpenAI.api_key = os.environ.get("OPENAI_API_KEY")

# If you have a custom endpoint or org, set them too:
# openai.api_base = ...
# openai.organization = ...
# client = OpenAI(
#     api_key=os.environ.get("OPENAI_API_KEY"),  # This is the default and can be omitted
# )

client = OpenAI()
def lambda_handler(event, context):
    main()

def main():
    """
    AWS Lambda entrypoint:
    1. Query unprocessed bulletins from bulletins_raw.
    2. Send them to GPT with system+user instructions.
    3. Parse the JSON response.
    4. Insert results into bulletins_processed or your schema of choice.
    """

    db_session = SessionLocal()
    try:
        # 1) Fetch unprocessed bulletins
        unprocessed_bulletins = db_session.query(BulletinRaw)\
            .filter(BulletinRaw.processed == False)\
            .order_by(BulletinRaw.batch_id, BulletinRaw.bulletin_number)\
            .all()

        if not unprocessed_bulletins:
            logger.info("No unprocessed bulletins found.")
            return {"statusCode": 200, "body": "No unprocessed bulletins."}

        # 2) Convert bulletins into the JSON array we’ll send to GPT
        bulletins_array = []
        for b in unprocessed_bulletins:
            bulletins_array.append({
                "batch_id": b.batch_id,
                "bulletin_number": b.bulletin_number,
                "date": b.date.isoformat() if b.date else "TBD",
                "description": b.description
            })

        # 3) Call GPT with system + user instructions
        # Provide the bulletins array as the "user" content. The system instructions
        # will match your big JSON schema requirement text from Playground
        # We'll define them in code for clarity:
        system_instructions = get_system_instructions()
        while bulletins_array:
            user_prompt = json.dumps(bulletins_array[:10], ensure_ascii=False, indent=2)

            logger.info(f"Sending {len(bulletins_array)} bulletins to GPT.")
            # 4) Run classification
            response_json,response_full = classify_bulletins(system_instructions, user_prompt)

            if not response_json:
                logger.error("No response or invalid JSON from GPT.")
                return {"statusCode": 500, "body": "GPT returned empty or invalid JSON."}

            # 5) Store results in bulletins_processed
            # The GPT response is expected to have a structure like:
            # {
            #   "bulletins": [
            #       {
            #         "batch_id": "...",
            #         "bulletin_number": "...",
            #         "location_report": "...",
            #         "location_event": "...",
            #         "date": "...",
            #         "time": "...",
            #         "category": "...",
            #         "sub_category": "..."
            #       }, ...
            #   ]
            # }
            gpt_bulletins = response_json.get("bulletins", [])

            # 6) Insert/Update each into DB
            inserted_count = 0
            for g_bull in gpt_bulletins:
                try:
                    # Convert IDs back to int if needed
                    b_id = int(g_bull["batch_id"])
                    bull_num = int(g_bull["bulletin_number"])

                    # Check if we already have a row in bulletins_processed
                    existing = db_session.query(BulletinProcessed)\
                        .filter_by(batch_id=b_id, bulletin_number=bull_num)\
                        .first()

                    raw_existing = db_session.query(BulletinRaw).filter_by(batch_id=b_id, bulletin_number=bull_num).first()

                    if not existing:
                        # Create new row
                        existing = BulletinProcessed(
                            batch_id=b_id,
                            bulletin_number=bull_num
                        )
                        db_session.add(existing)

                    # Update fields from GPT
                    # existing.date = datetime.strptime(raw_existing.date, "%Y-%m-%d").date() \
                    #     if g_bull["date"] != "TBD" else None
                    existing.date = raw_existing.date
                    existing.description = raw_existing.description  # or replicate if you want

                    existing.location_report = g_bull["location_report"]
                    existing.lat_report , existing.lon_report = get_coordinates(existing.location_report)

                    existing.location_event = g_bull["location_event"]
                    existing.lat_event, existing.lon_event = get_coordinates(existing.location_event)

                    existing.category = g_bull["category"]
                    existing.sub_category = g_bull["sub_category"]
                    existing.notes = ""       # or store raw notes from GPT


                    date_str = g_bull["date"]
                    time_str = g_bull["time"]
                    if date_str != "TBD" and time_str != "TBD":
                        # "2025-01-02 15:00:00" -> datetime object

                        dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
                        existing.event_time = dt
                    else:
                        existing.event_time = datetime.strptime(f"{date_str}", "%Y-%m-%d")  # or handle however you want


                    existing.processor_version = response_full.model
                    existing.processed_timestamp = datetime.now()
                    # event_time if you want:
                    # existing.event_time = some parse from g_bull["time"] if not "TBD"
                    # etc...

                    # Mark raw as processed if you want
                    db_session.query(BulletinRaw).filter_by(batch_id=b_id, bulletin_number=bull_num)\
                        .update({"processed": True})
                    inserted_count += 1
                except Exception as ex:
                    logger.error(f"Error updating bulletins_processed for batch_id {g_bull.get('batch_id')} "
                                 f"bulletin_num {g_bull.get('bulletin_number')}: {ex}")
                    continue

            db_session.commit()
            msg = f"Successfully processed {inserted_count} bulletins from GPT classification."
            logger.info(msg)
            del bulletins_array[:10]
        return {"statusCode": 200, "body": msg}

    except Exception as e:
        logger.error(f"Unexpected error in lambda_handler: {e}")
        traceback.print_exc()
        return {"statusCode": 500, "body": "Internal Server Error"}
    finally:
        db_session.close()

def classify_bulletins(system_instructions, user_json_text):
    """
    Sends the bulletins to GPT chat completions with the system instructions
    and user content = user_json_text.
    Expects a strict JSON response.
    Returns the parsed Python dict or None if something fails.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # or the model you have
            messages=[
                {
                    "role": "system",
                    "content": system_instructions
                },
                {
                    "role": "user",
                    "content": user_json_text
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "my_schema",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "bulletins": {
                                "type": "array",
                                "description": "An array of bulletin reports.",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "batch_id": {
                                            "type": "string",
                                            "description": "A unique identifier for the batch of bulletins."
                                        },
                                        "bulletin_number": {
                                            "type": "string",
                                            "description": "The sequence number of the bulletin in the batch."
                                        },
                                        "location_report": {
                                            "type": "string",
                                            "description": "Detailed description of the reported location including city or region, as its writen in Macedonian."
                                        },
                                        "location_event": {
                                            "type": "string",
                                            "description": "Detailed description of the event location including city or region, as its writen in Macedonian."
                                        },
                                        "date": {
                                            "type": "string",
                                            "description": "The date of the event in YYYY-MM-DD format."
                                        },
                                        "time": {
                                            "type": "string",
                                            "description": "The time of the event in HH:MM:SS format."
                                        },
                                        "category": {
                                            "type": "string",
                                            "description": "The main category of the bulletin/report."
                                        },
                                        "sub_category": {
                                            "type": "string",
                                            "description": "The specific sub-category of the bulletin/report."
                                        }
                                    },
                                    "required": [
                                        "batch_id",
                                        "bulletin_number",
                                        "location_report",
                                        "location_event",
                                        "date",
                                        "time",
                                        "category",
                                        "sub_category"
                                    ],
                                    "additionalProperties": False
                                }
                            }
                        },
                        "required": [
                            "bulletins"
                        ],
                        "additionalProperties": False
                    }
                }
            },
            temperature=1,
            max_tokens=16383,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        # The response is typically in response.choices[0].message.content
        # print(response.choices[0].message.content)
        content = response.choices[0].message.content
        print(response)
        # Parse the JSON
        parsed = json.loads(content)
        return parsed,response
    except Exception as e:
        logger.error(f"Error calling OpenAI: {e}")
        return None

geocoder = GeoCoder()
geocode_cache = {}
def get_coordinates(location):
    try:
        if location in geocode_cache:
            latitude, longitude = geocode_cache[location]
        else:
            latitude, longitude = geocoder.geocode_location(location)
            geocode_cache[location] = (latitude, longitude)
        return latitude, longitude

    except Exception as e:
        logging.error(f"Geocoding failed for location '{location}': {e}")
        latitude, longitude = None, None
        return latitude, longitude

def get_system_instructions():
    """
    Return a large string with your system instructions exactly how you do
    in Playground. This includes categories, JSON schema, etc.
    You can store it in a separate file or env var if it's huge.
    """
    instructions = """# System Instructions

You are part of a **police bulletin program**. Your job is to:

1. **Read an array of bulletins** (each containing a `batch_id`, `bulletin_number`, `date`, and a text `description` in Macedonian).  
2. For **each** bulletin in the array, extract and provide the following fields in a **single JSON** response:
   - `batch_id`  
   - `bulletin_number`  
   - `location_report`: A textual description of **where the bulletin/report was made** (location of the report made, usually a police station; if possible, include street first, then city/region).  
   - `location_event`: A textual description of **where the incident took place** (if possible, list from more specific to broader: e.g., street, neighborhood, then city, region).  
   - `date` (in `YYYY-MM-DD` format).  
   - `time` (in `HH:MM:SS` format).  
   - `category` (choose **one** primary category from the list below).  
   - `sub_category` (a more specific subcategory, if applicable).

3. Output all processed bulletins as an **array** under a top-level key `"bulletins"`.  
4. **Follow a strict JSON schema** which requires each bulletin to have the fields listed above (and **no** additional fields).

---

## Categories and Subcategories

When determining the `category` and `sub_category`, choose the **best match** from the following **16** main categories. If an offense is **not** clearly listed, or you’re uncertain, you may use **“Other / Miscellaneous”**. Only **one** category and sub-category per bulletin—pick the **primary** offense.

1. **Crimes Against Life and Body**  
   - Homicide (Murder, Manslaughter, Infanticide)  
   - Attempted Homicide  
   - Physical Assault/Battery (Simple, Aggravated)  
   - Domestic Violence  
   - Kidnapping/Abduction  
   - Bodily Harm (Light or Serious)

2. **Sexual Offenses**  
   - Rape  
   - Sexual Assault  
   - Child Sexual Abuse  
   - Sexual Harassment  
   - Indecent Exposure  
   - Sexual Exploitation

3. **Crimes Against Freedom and Rights**  
   - Illegal Deprivation of Liberty  
   - Threats/Harassment/Stalking  
   - Blackmail/Extortion  
   - Violation of Privacy

4. **Crimes Against Family and Minors**  
   - Child Abuse/Neglect  
   - Child Abduction  
   - Violation of Family Obligations  
   - Domestic Child Endangerment

5. **Property Offenses**  
   - Theft/Larceny  
   - Burglary/Unlawful Entry  
   - Robbery  
   - Arson  
   - Vandalism  
   - Handling Stolen Goods  
   - Motor Vehicle Theft  
   - Shoplifting

6. **Drug-Related Offenses**  
   - Possession  
   - Trafficking/Dealing  
   - Cultivation/Manufacturing  
   - Distribution  
   - Drug Paraphernalia

7. **Weapons & Explosives Offenses**  
   - Illegal Possession of Firearms/Explosives  
   - Weapons Trafficking  
   - Unlawful Use/Discharge of a Weapon

8. **Fraud, Forgery & Financial Crimes**  
   - General Fraud (credit card, check, etc.)  
   - Forgery/Counterfeiting (documents, currency)  
   - Embezzlement  
   - Money Laundering  
   - Corruption/Bribery  
   - Identity Theft

9. **Public Order Offenses**  
   - Disturbing the Peace  
   - Public Intoxication  
   - Prostitution/Solicitation  
   - Unauthorized Public Gathering  
   - Offensive Behavior  
   - Incitement of Violence

10. **Traffic & Vehicle Offenses**  
    - Driving Under the Influence (DUI)  
    - Reckless Driving  
    - Hit-and-Run  
    - Unlicensed Driving

11. **Environmental Crimes**  
    - Pollution  
    - Illegal Logging  
    - Wildlife Offenses  
    - Violation of Environmental Regulations

12. **Organized Crime**  
    - Racketeering  
    - Participation in Organized Crime  
    - Human Trafficking  
    - Terrorism-Related Activities

13. **Missing Persons**  
    - Missing Person Report  
    - Found Person

14. **Crimes Against Official Duty or Justice**  
    - Abuse of Official Position  
    - Obstruction of Justice  
    - False Testimony / Perjury  
    - Falsification

15. **Cybercrime**  
    - Unauthorized Access / Hacking  
    - Phishing  
    - Cyberstalking  
    - Identity/Data Theft

16. **Other / Miscellaneous**  
    - Licensing Violations  
    - Public Health Violations  
    - Incident Involving An Animal
    - Any other specialized violations not covered above

---

## Formatting & Extraction Rules

1. **Date**  
   - Use `YYYY-MM-DD` format.  
   - If the bulletin date/time is uncertain, **approximate** or use `TBD`.

2. **Time**  
   - Use `HH:MM:SS` (24-hour format).  
   - If only hour and minute exist, append `:00`.  
   - If no time is given, default to `"00:00:00"` or `"TBD"`.

3. **Location Fields**  
   - **location_report**: Where the bulletin says the report was made (or filed). Prefer the format: `StreetName, City` if possible.  
   - **location_event**: Where the incident itself took place, again from more specific to broader (`StreetName, City`, etc.).  
   - If only one location is mentioned, use it for both fields unless clearly stated otherwise.  
   - If unknown, set `"Unknown"` or `"TBD"`.

4. **Category**  
   - Exactly **one** from the list above.  
   - If unsure, **“Other / Miscellaneous.”**

5. **Sub-Category**  
   - Should match the chosen category.  
   - If uncertain, **“Other / Miscellaneous.”**

6. **Output**  
   - Return **one** JSON object with top-level key `"bulletins"`.  
   - `"bulletins"` must be an **array** of objects, each containing the required fields (no extras).

7. **Language**  
   - Use Macedonian for location names if that’s how they appear.  
   - Use English for `category` and `sub_category` from the enumerated list.

8. **Strict JSON**  
   - No extra commentary, no markdown, no additional keys.  
   - Just the required fields in a valid JSON structure.

"""
    return instructions



if __name__ == "__main__":
    for _ in range(0,10):
        main()