from google.cloud import monitoring_v3
from google.protobuf.timestamp_pb2 import Timestamp
# import datetime
import pytz
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
from datetime import datetime, timedelta, timezone


def get_cloud_run_metrics(metric_type, resource_type, start_time,end_time,number_interval,project_id="tsmccareerhack2024-icsd-grp2",
                            service_name = "hedgedoc"):
    """
    Get Cloud Run metrics for a specific metric type within a given time range.

    Args:
        project_id (str): The Google Cloud project ID.
        metric_type (str): The metric type to retrieve.
        resource_type (str): The resource type, for example, "cloud_run_revision".
        start_time (datetime): The start time of the time range.
        end_time (datetime): The end time of the time range.

    Returns:
        pd.DataFrame: A DataFrame containing the retrieved metrics.
    """
    client = monitoring_v3.MetricServiceClient()
    # Convert start_time and end_time to Timestamp objects
    start_timestamp = Timestamp()
    start_timestamp.FromDatetime(start_time)
    end_timestamp = Timestamp()
    end_timestamp.FromDatetime(end_time)
    interval= monitoring_v3.TimeInterval(start_time=start_timestamp, end_time=end_timestamp)
    results = client.list_time_series(
        name=f'projects/{project_id}',
        filter=f"metric.type=\"{metric_type}\" resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"{service_name}\"",
        interval=interval
    )
    
    data = []
    result_df = pd.DataFrame()
    target_timezone_offset = timezone(timedelta(hours=8))
    

    for time_series in results:
        for point in time_series.points:
            utc_timestamp = datetime.fromtimestamp(point.interval.end_time.timestamp())
            taiwan_timestamp = utc_timestamp.astimezone(target_timezone_offset).replace(second=0,microsecond=0).strftime('%Y-%m-%d %H:%M:%S%z')
            try:
                if "count" in metric_type:
                    value = point.value.int64_value
                elif "utilizations" in metric_type or "latencies" in metric_type:
                    try:
                        value = point.value.distribution_value.mean
                    except ValueError:
                        value = 0.0
            except ValueError:
                value = 0.0

            data.append({
                'timestamp': taiwan_timestamp,
                f'{metric_type}': value,
            })
    
    if data == []:
        result_df[metric_type] = [0]* number_interval
    else:
        result_df = pd.DataFrame(data)
    return result_df

def run_time_interval(metric_types,type_interval,number_interval,start_time,end_time,
                        project_id = "tsmccareerhack2024-icsd-grp2", service_name = "hedgedoc",resource_type = "cloud_run_revision"):
    """
    Run multiple Cloud Run metrics retrieval tasks in parallel for a specified time interval.

    Args:
        project_id (str): The Google Cloud project ID.
        metric_types (list): A list of metric types to retrieve.
        resource_type (str): The resource type, for example, "cloud_run_revision".
        start_time (datetime): The start time of the time range.
        end_time (datetime): The end time of the time range.

    Returns:
        pd.DataFrame: A DataFrame containing combined metrics from all specified metric types.
    """
    with ThreadPoolExecutor() as executor:
        # Submit tasks for each metric
        futures = {executor.submit(get_cloud_run_metrics,metric_type, resource_type, start_time,end_time,number_interval): metric_type for metric_type in metric_types}
        # Collect results as they become available
        results = {metric: future.result() for future, metric in futures.items()}
    #Ensure consistent timestamp format and column names
    result_dict = {}
    for metric, df in results.items():
        result_dict[metric] = df[metric].to_list()
    df1 = pd.DataFrame(result_dict[metric_types[0]])
    return df1


def metric_range(project_id='tsmccareerhack2024-icsd-grp2', service_name ='hedgedoc',
                 resource_type = 'cloud_run_revision', type_interval = 'minutes', number_interval = 60, metric_ = "cpu"):

    metric = {  "cpu" : 'run.googleapis.com/container/cpu/utilizations',
                "memory" : 'run.googleapis.com/container/memory/utilizations',
                "RequestCount" : 'run.googleapis.com/request_count',
                "RequestLatency" : 'run.googleapis.com/container/startup_latencies'
    }

    # 使用字符串的 split() 方法将其分割成子字符串列表
    substrings = metric_.split(',')
    # 创建一个包含子字符串的列表
    sub_ = [substring.split() for substring in substrings]
    metric_types = []

    for i in range(len(sub_)):
        metric_types.append(metric[sub_[i][0]])
    end_time = datetime.utcnow().replace(second=0,microsecond=0)

    if type_interval == 'minutes':
        start_time = (end_time - timedelta(minutes=number_interval))
    else:
        start_time = (datetime.utcnow() - timedelta(hours=number_interval))
    # result_df_1 , result_df_2 = run_time_interval(metric_types,type_interval,number_interval,start_time,end_time)
    # return result_df_1 , result_df_2
    result_df_1 = run_time_interval(metric_types,type_interval,number_interval,start_time,end_time)
    return result_df_1

# result_df_1  = metric_range(metric_ = "RequestCount")
