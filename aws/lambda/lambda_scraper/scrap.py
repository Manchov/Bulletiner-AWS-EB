# scrap.py

import requests
from bs4 import BeautifulSoup
import re
import random
import time
from datetime import datetime
import logging
from tenacity import retry, wait_exponential, stop_after_attempt
from database import SessionLocal
from models import BulletinBatch, BulletinRaw
from sqlalchemy.exc import SQLAlchemyError

# List of User-Agent strings for rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.64'
]

# Initialize logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@retry(wait=wait_exponential(min=1, max=10), stop=stop_after_attempt(5), reraise=True)
def get_response(session, url, headers):
    """Sends HTTP GET with retries/exponential backoff."""
    response = session.get(url, headers=headers, timeout=(5, 10))
    response.raise_for_status()
    return response

# ---------------------------------------------------------------------------
# Content extraction helper functions
# ---------------------------------------------------------------------------
def get_content_container(soup):
    """
    Try several selectors until one returns content.
    """
    container = soup.find('span', id='MainContent_litNaslov')
    if container:
        return container
    container = soup.find('div', class_='singleleft_inner')
    if container:
        return container
    # Fallback to the whole body (less ideal)
    return soup.body

def clean_text(txt):
    """
    Cleans text by replacing non-breaking spaces, merging newlines and spaces.
    """
    txt = txt.replace('\xa0', ' ')
    txt = re.sub(r'[\r\n]+', '\n', txt)
    txt = re.sub(r'[ \t]+', ' ', txt)
    return txt.strip()

def split_into_bulletins_text_nodes(soup):
    """
    Extracts bulletins by retrieving all text nodes (i.e. #text) from the content container.
    Each non-empty text node is cleaned and returned as an individual bulletin.
    """
    container = get_content_container(soup)
    if not container:
        return []
    text_nodes = container.find_all(text=True)
    # Clean each node and filter out empty strings.
    bulletins = [clean_text(node) for node in text_nodes if node.strip()]
    return bulletins

def parse_date_from_title(title_text):
    """
    Extracts a date in dd.mm.yyyy format from the title text.
    Returns a datetime.date or None.
    """
    match = re.search(r'\b(\d{2}\.\d{2}\.\d{4})\b', title_text)
    if match:
        try:
            return datetime.strptime(match.group(1), '%d.%m.%Y').date()
        except ValueError:
            pass
    return None

# ---------------------------------------------------------------------------
# Database saving helper functions
# ---------------------------------------------------------------------------
def save_bulletin_batch(db_session, post_id, scraped, scrapable, date_val, count, note):
    """
    Inserts or updates the batch row in bulletin_batches.
    """
    from datetime import datetime
    try:
        batch = db_session.query(BulletinBatch).filter_by(batch_id=post_id).first()
        if batch:
            batch.scraped = scraped
            batch.scrapable = scrapable
            batch.date = date_val
            batch.date_scraped = datetime.utcnow()
            batch.bulletin_count = count
            batch.note = note
        else:
            batch = BulletinBatch(
                batch_id=post_id,
                scraped=scraped,
                scrapable=scrapable,
                date=date_val,
                date_scraped=datetime.utcnow(),
                bulletin_count=count,
                note=note
            )
            db_session.add(batch)
        db_session.commit()
    except SQLAlchemyError as e:
        db_session.rollback()
        logger.error(f"Database error while saving batch {post_id}: {e}")

def save_bulletins_raw(db_session, events, post_id):
    """
    Inserts or updates bulletins into bulletins_raw with (batch_id, bulletin_number).
    """
    try:
        batch = db_session.query(BulletinBatch).filter_by(batch_id=post_id).first()
        if not batch:
            logger.error(f"No batch found for post_id {post_id}")
            return

        for ev in events:
            existing_record = (
                db_session.query(BulletinRaw)
                .filter_by(batch_id=post_id, bulletin_number=ev["bulletin_number"])
                .first()
            )
            if existing_record:
                existing_record.date = ev["date"]
                existing_record.description = ev["description"]
                existing_record.processed = False
            else:
                br = BulletinRaw(
                    batch_id=post_id,
                    bulletin_number=ev["bulletin_number"],
                    date=ev["date"],
                    description=ev["description"],
                    processed=False
                )
                db_session.add(br)
        db_session.commit()

    except SQLAlchemyError as e:
        db_session.rollback()
        logger.error(f"Database error while saving bulletins for batch {post_id}: {e}")

# ---------------------------------------------------------------------------
# Main bulletin fetching function using the new text nodes method
# ---------------------------------------------------------------------------
def fetch_bulletin(url, post_id, session=None, db_session=None):
    """
    Main function to scrape the bulletins for a given post_id using the text nodes method.
    - Downloads the page.
    - Parses the date from the page title.
    - Extracts all text nodes from the content container.
    - Treats each non-empty text node as a separate bulletin.
    - Saves the bulletins and related batch info to the DB.
    """
    session = session or requests.Session()
    db_session = db_session or SessionLocal()

    try:
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        response = get_response(session, url + str(post_id), headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        # 1) Parse date from the page title.
        title_elem = soup.find('span', id='MainContent_lblNaslov')
        title_text = title_elem.get_text(strip=True) if title_elem else ""
        date_val = parse_date_from_title(title_text)

        # 2) Extract bulletins using the text nodes method.
        bulletins = split_into_bulletins_text_nodes(soup)

        # 3) Build the final list of events.
        events = []
        for i, bulletin_text in enumerate(bulletins, start=1):
            if bulletin_text:
                events.append({
                    'bulletin_number': i,
                    'date': date_val,
                    'description': bulletin_text
                })

        bulletin_count = len(events)
        scrapable = bulletin_count > 1
        note = ("Scraped successfully" if scrapable
                else ("Only one bulletin - recheck" if bulletin_count == 1
                      else "No bulletins extracted"))

        # 4) Save batch and bulletin records to the DB.
        save_bulletin_batch(db_session, post_id, True, scrapable, date_val, bulletin_count, note)
        if events:
            save_bulletins_raw(db_session, events, post_id)

        return events

    except Exception as e:
        logger.exception(f"Error scraping post_id {post_id}: {e}")
        note = f"Error: {e}"
        save_bulletin_batch(db_session, post_id, False, False, None, 0, note)
        return []
    finally:
        delay = random.uniform(1, 5)
        logger.info(f"Waiting for {delay:.2f} seconds before the next request...")
        time.sleep(delay)
        db_session.close()

# ---------------------------------------------------------------------------
# (Optional) If you want to test this module directly:
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    test_url = "https://mvr.gov.mk/izvadok-od-dnevni-nastani/"
    # Replace with a valid post_id for testing, for example 3572
    test_post_id = 3572
    events = fetch_bulletin(test_url, test_post_id)
    for event in events:
        print(f"Bulletin #{event['bulletin_number']}: {event['description'][:200]}")
