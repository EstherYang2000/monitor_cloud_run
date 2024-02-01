from google.auth import default
from google.cloud.monitoring_v3.services.query_service import QueryServiceClient
from google.cloud.monitoring_v3.types import metric_service
from google.cloud import monitoring_v3
import pandas as pd
import pytz
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from RealTimeErrorDetect import *
from AssemblePrompt import *
from log_analyze import *
from genAITranslator import *
from sendEmail import *
from real_time_log import *


def fetch_metric_data(project_id, metric_type, type_interval, number_interval):
    """
    Fetches Cloud Run metrics using Monitoring Query Language (MQL) and creates a DataFrame.

    Args:
    - project_id (str): Google Cloud Project ID.
    - metric_type (str): Metric type to fetch.
    - type_interval (str): Interval in seconds, minutes, or hours.
    - number_interval (int): Number of intervals.

    Returns:
    - pd.DataFrame: A DataFrame with time as the index and metrics as columns.
    """
    # Set the credentials for google-cloud-monitoring library
    credentials, _ = default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
    query = ''
    # Build the MQL query
    if 'utilizations' in metric_type :  #container/cpu/utilizations,container/memory/utilizations
        query = f'''fetch cloud_run_revision
        | metric '{metric_type}'
        | filter (resource.service_name == 'hedgedoc')
        | align delta({number_interval}{type_interval[0]})
        | every {number_interval}{type_interval[0]}
        | group_by [], [value_utilizations_mean: mean(value.utilizations)]'''

    elif 'startup_latencies' in metric_type : #container/startup_latencies
        query=f"""
            fetch cloud_run_revision
            | metric '{metric_type}'
            | align delta({number_interval}{type_interval[0]})
            | every {number_interval}{type_interval[0]}
            | group_by [], [value_startup_latencies_mean: mean(value.startup_latencies)]         
        
        """
    elif 'request_latencies' in metric_type : #request_latencies
        query=f"""
            fetch cloud_run_revision
            | metric '{metric_type}'
            | align delta({number_interval}{type_interval[0]})
            | every {number_interval}{type_interval[0]}
            | group_by [], [value_request_latencies_mean: mean(value.request_latencies)]        
                    
        """
        
    elif 'request_count' in metric_type: #request_count
        query =f"""
        fetch cloud_run_revision
        | metric '{metric_type}'
        | align delta({number_interval}{type_interval[0]})
        | every {number_interval}{type_interval[0]}
        | group_by [], [value_request_count_aggregate: aggregate(value.request_count)]
        
        """ 
        
    elif 'instance_count' in metric_type: #container/instance_count
        query =f"""
        fetch cloud_run_revision
        | metric '{metric_type}'
        | group_by {number_interval}{type_interval[0]}, [value_instance_count_mean: mean(value.instance_count)]
        | every {number_interval}{type_interval[0]}
        | group_by [],
            [value_instance_count_mean_aggregate: aggregate(value_instance_count_mean)]
        """            
    # Build the QueryTimeSeriesRequest
    metric_query = metric_service.QueryTimeSeriesRequest(name=f'projects/{project_id}', query=query)

    # Create a QueryServiceClient
    service_client = QueryServiceClient()
    # Execute the query
    results = service_client.query_time_series(metric_query)
    # Process the response and create a list of data points
    data = []
    taiwan_time_zone = pytz.timezone('Asia/Taipei')  # Set the desired time zone
    if results.time_series_data:
        for time_series_entry in results.time_series_data:
            for point_data in time_series_entry.point_data:
                # time_interval = point_data.time_interval.start_time
                values = point_data.values
                for value in values:  # Iterate over the repeated field
                    utc_timestamp = datetime.fromtimestamp(point_data.time_interval.start_time.timestamp()).replace(tzinfo=pytz.UTC)
                    taiwan_timestamp = utc_timestamp.astimezone(taiwan_time_zone).strftime('%Y-%m-%d %H:%M:%S%z')
                    value_value = value.double_value  # Assuming 'double_value' is the correct attribute, adjust if needed
                    
                    data.append({"Timestamp": taiwan_timestamp, f"{metric_type}": value_value})
        # Create a DataFrame
    else:
        current_time = datetime.now(taiwan_time_zone).strftime('%Y-%m-%d %H:%M:%S%z')
        data.append({"Timestamp": current_time, f"{metric_type}": 0.0})  
    df = pd.DataFrame(data)

    return df
def run_mql_queries(metric_types,type_interval,number_interval,project_id):
    """
    Fetches multiple Cloud Run metrics concurrently using Monitoring Query Language (MQL).

    Args:
    - project_id (str): Google Cloud Project ID.
    - metric_types (list of str): List of metric types to fetch.
    - type_interval (str): Interval in seconds, minutes, or hours.
    - number_interval (int): Number of intervals.

    Returns:
    - pd.DataFrame: A DataFrame with timestamps as the index and metrics as columns.
    """
    # Use ThreadPoolExecutor to run fetch_metric_data concurrently for each metric
    with ThreadPoolExecutor() as executor:
        # Submit tasks for each metric
        futures = {executor.submit(fetch_metric_data, project_id, metric, type_interval, number_interval): metric for metric in metric_types}

        # Collect results as they become available
        results = {metric: future.result() for future, metric in futures.items()}

    # Ensure consistent timestamp format and column names
    for metric, df in results.items():
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])  # Convert to datetime if not already
        df.set_index('Timestamp', inplace=True)            
    # Concatenate the DataFrames into one based on the timestamp (index)
    combined_df = pd.concat(results.values(), axis=1, join='outer')
    combined_df.reset_index(inplace=True)    
    return combined_df    