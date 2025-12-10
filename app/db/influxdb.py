from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from app.core.config import settings

class InfluxDB:
    client: InfluxDBClient = None
    write_api = None
    query_api = None

influxdb = InfluxDB()

def connect_to_influxdb():
    """Connect to InfluxDB"""
    print("Connecting to InfluxDB...")
    influxdb.client = InfluxDBClient(
        url=settings.influxdb_url,
        token=settings.influxdb_token,
        org=settings.influxdb_org
    )
    influxdb.write_api = influxdb.client.write_api(write_options=SYNCHRONOUS)
    influxdb.query_api = influxdb.client.query_api()
    print(f"Connected to InfluxDB: {settings.influxdb_org}")

def close_influxdb_connection():
    """Close InfluxDB connection"""
    print("Closing InfluxDB connection...")
    if influxdb.client:
        influxdb.client.close()
    print("InfluxDB connection closed")

def get_write_api():
    """Get write API instance"""
    return influxdb.write_api

def get_query_api():
    """Get query API instance"""
    return influxdb.query_api