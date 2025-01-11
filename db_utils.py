from datetime import datetime
import pymongo
from config import config


def get_client() -> pymongo.MongoClient:
    return pymongo.MongoClient(
        config['db_host'],
        config['db_port'],
        username=config['db_user'],
        password=config['db_pass'],
        authSource='admin',
        authMechanism='SCRAM-SHA-1',
        connect=False,
        tls=True, tlsAllowInvalidCertificates=True
    )


def location_log(timestamp: datetime, name: str, cat_id: int, enter: bool, location: str):
    client = get_client()
    client['catwar']['movement'].insert_one({
        'timestamp': timestamp,
        'cat_name': name,
        'cat_id': cat_id,
        'action': 'перешел(а) на локацию' if enter else 'покинул(а) локацию',
        'location': location
    })
