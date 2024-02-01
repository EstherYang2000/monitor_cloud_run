import sys
sys.path.append('/home/icsd_user05_tsmc_hackathon_cloud/app/monitor/functions')

from RealTimeErrorDetect import *
from AssemblePrompt import *
from log_analyze import *
from genAITranslator import *
from sendEmail import *
from real_time_log import *
from config import load_config
from mql_metric_minute import run_mql_queries
import time

# run time
start＿_time = time.time()

# 讀入config檔案

config = load_config()
project_id = config['GCP']['project_id']
metric_types = [
    'run.googleapis.com/container/cpu/utilizations', #v
    'run.googleapis.com/container/instance_count', #
    'run.googleapis.com/container/memory/utilizations', #v
    'run.googleapis.com/container/startup_latencies', #v
    'run.googleapis.com/request_count', #
    'run.googleapis.com/request_latencies'#v
]

# 抓取即時metrics
type_interval = 'minutes'
number_interval = 1
result_df = run_mql_queries(metric_types,type_interval,number_interval,project_id)

# metrics沒抓到值就補0
for i in range(1,7):
    if result_df.iloc[0,i] == 'Nan':
        result_df.iloc[0,i] = 0

#時間 #cpu #instance_count #memory #startup_latencies #request_count #request_latencies
result_df.iloc[0,1:7] = result_df.iloc[0,1:7].astype(float)


# Prompt , has_scale_up = getPrompt(cpu_utilization0,cpu_utilization1,memory_utilization0,memory_utilization1,
#                       restart,InstanceCount,new_RequestCount,new_RequestLatency)
P , cpu_s,cpu_m = getPrompt(result_df.iloc[0,1],result_df.iloc[0,3],
                        result_df.iloc[0,4],result_df.iloc[0,2],result_df.iloc[0,5],result_df.iloc[0,6])



# logging部分
logging = log_catch(str(result_df.iloc[0,0]))

if logging!=None:
    log = analyze_main_ontime(logging)
else:
    log = False

# 結合metrics和logging給出Prompts
response = assemblePrompts(P,log)

# 有異常就寄信
if response:
    text = interview(response)
    send_email(result_df.iloc[0,0],"alert", text, "sharon.lin.2001@gmail.com",cpu_s,cpu_m)
    # send_email(result_df.iloc[0,0],"alert", text, "THHSUY@TSMC.COM",cpu_s,cpu_m) 

# 計算run time
end_time = time.time()
run_time = end_time - start_＿time

print(f"運行時間為: {run_time} 秒")

