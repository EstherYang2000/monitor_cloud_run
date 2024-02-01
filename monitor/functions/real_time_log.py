from google.cloud import logging_v2
from google.protobuf.timestamp_pb2 import Timestamp
from datetime import datetime, timedelta, timezone
import pytz
import time
import json
def convert_to_taiwan_timezone(timestamp_str):
    # Parse the string representation to a datetime object
    dt = datetime.datetime.fromisoformat(timestamp_str)

    # Convert to Taiwan timezone
    taiwan_timezone = pytz.timezone('Asia/Taipei')
    dt_taiwan = dt.replace(tzinfo=pytz.utc).astimezone(taiwan_timezone)

    return dt_taiwan.isoformat()

def fetch_cloud_run_logs(project_id, service_name, region, end_time_str):
    client = logging_v2.Client(project=project_id)
    # Convert end_time_str to a datetime object
    end_time_tw = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S%z')
    # # Convert end_time to UTC timezone
    end_time_utc = end_time_tw.astimezone(pytz.utc)    
    taiwan_time_zone = pytz.timezone('Asia/Taipei')  # Set the desired time zone
    time_format = "%Y-%m-%dT%H:%M:%S.%f%z"
    start_time_utc = end_time_utc - timedelta(minutes=1)

    
    filter_str = (
        f'resource.type="cloud_run_revision"'
        f' AND resource.labels.service_name="{service_name}"'
        f' AND timestamp>="{start_time_utc.strftime(time_format)}"'
        f' AND timestamp<="{end_time_utc.strftime(time_format)}"'
        f' AND (severity="WARNING" OR severity="ERROR" OR severity="CRITICAL" OR severity="ALERT" OR severity="EMERGENCY")'
    )
    entries = client.list_entries(filter_=filter_str, page_size=1000)
    # for entry in filtered_entries:
    error_list = []
    for entry in entries:

        # Convert StructEntry to JSON
        entry_json = json.dumps(entry.to_api_repr(), indent=2)
        entry_dict = json.loads(entry_json)
        error_list.append(entry_dict)
        return error_list
def log_catch(end_time_str):
    # Replace these values with your actual project, service, and region
    project_id = 'tsmccareerhack2024-icsd-grp2'
    service_name = 'hedgedoc'
    region = 'asia-east1 '
    error_list = fetch_cloud_run_logs(project_id, service_name, region, end_time_str)
    return error_list
