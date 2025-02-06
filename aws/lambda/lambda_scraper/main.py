# lambda_scraper\main.py
import os

import scrap
from database import SessionLocal
import time
import random
import requests
import logging
import yaml
from models import BulletinBatch
from sqlalchemy import create_engine,func
from sqlalchemy.orm import sessionmaker

# Initialize logging
# logger = logging.getLogger(__name__)
logger = logging
logger.getLogger(__name__)
logger.basicConfig(level=logging.INFO)

def get_scraped_ids(db_session):
    # scraped_batches = db_session.query(BulletinBatch.batch_id).all()
    scraped_batches = db_session.query(BulletinBatch.batch_id).filter(BulletinBatch.scraped==True).all()
    return [item[0] for item in scraped_batches]


def get_latest_batch_id(db_session):
    """
    Returns the maximum batch_id in bulletin_batches where scraped=True.
    If none found, returns fallback (e.g., 3572).
    """
    result = db_session.query(
        func.max(BulletinBatch.batch_id)
    ).filter(
        BulletinBatch.scraped == True
    ).scalar()

    return result if result else 3572

def main():
    # Load configurations
    # with open('config.yaml', 'r') as f:
    #     config = yaml.safe_load(f)

    # url = config['base_url']
    url = os.environ.get("BASE_URL")
    # request_limit = config['request_limit']
    request_limit = 30
    # dateID = {k: range(*v) for k, v in config['dateID'].items()}

    session = requests.Session()  # Use a session to manage requests
    db_session = SessionLocal()

    print(f"latest id is {get_latest_batch_id(db_session)}")

    all_ids_list = get_scraped_ids(db_session)

    request_count = 0

    # date_search = dateID["2015"]
    latest_batch_id = get_latest_batch_id(db_session)
    search_error_reach = 1+3
    date_search = range(latest_batch_id, latest_batch_id + search_error_reach)

    for post_id in date_search:
        if post_id in all_ids_list:
            logger.info(f'Skipping post_id {post_id} (Already scraped)')
            continue

        logger.info(f'Scraping post_id {post_id}')
        events = scrap.fetch_bulletin(url, post_id, session, db_session)
        logger.info(f'Number of events scraped: {len(events)}')

        request_count += 1
        if request_count >= request_limit:
            logger.info(f'Reached request limit of {request_limit}. Stopping the session.')
            break

    db_session.close()

def lambda_handler(event, context):
    main()

if __name__ == "__main__":
    main()
