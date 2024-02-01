#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from datetime import datetime, timedelta
import os
import vertexai
from vertexai.language_models import TextGenerationModel
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import markdown2
start＿_time = time.time()
def checkCPUutilization(filename):
    """
    Container CPU Utilization (%) > 60
    紀錄所有異常時間
    """
    cpu_utilization = pd.read_csv(filename)
    cpu_utilization.columns.values[1] = 'Container CPU Utilization (%)'
    cpu_utilization.iloc[:, 1] = cpu_utilization.iloc[:, 1].astype(float)
    cpu_utilization_threshold = 60
    cpu_utilization_size = cpu_utilization.shape[0]
    cpu_utilization_error_time = []
    for i in range(1, cpu_utilization_size):
        if cpu_utilization.iloc[i,1] > cpu_utilization_threshold and cpu_utilization.iloc[i-1,1] > cpu_utilization_threshold:
            cpu_utilization_error_time.append(cpu_utilization.iloc[i,0])
    return cpu_utilization_error_time


def checkMEMORYutilization(filename):
    """
    Container Memory Utilization (%) > 60
    紀錄所有異常時間
    """
    memory_utilization = pd.read_csv(filename)
    memory_utilization.columns.values[1] = 'Container memory Utilization (%)'
    memory_utilization.iloc[:, 1] = memory_utilization.iloc[:, 1].astype(float)
    memory_utilization_threshold = 60
    memory_utilization_size = memory_utilization.shape[0]
    memory_utilization_error_time = []
    for i in range(1, memory_utilization_size):
        if memory_utilization.iloc[i,1] > memory_utilization_threshold and memory_utilization.iloc[i-1,1] > memory_utilization_threshold:
            memory_utilization_error_time.append(memory_utilization.iloc[i,0])
    return memory_utilization_error_time


def checkCloudRunReStart(filename):
    """
    Cloud run re-start
    紀錄所有重啟時間
    """
    startup_latency = pd.read_csv(filename)
    startup_latency.columns.values[1] = 'Container Startup Latency (ms)'
    startup_latency.iloc[:, 1] = startup_latency.iloc[:, 1].astype(float)
    return list(startup_latency.iloc[:, 0])


def checkInstanceCount(filename):
    """
    Instance count > 2
    紀錄所有異常時間
    """
    instance_count = pd.read_csv(filename)
    instance_count.iloc[:, 1] = instance_count.iloc[:, 1].astype(int)   
    summed_columns = instance_count.iloc[:, 1:].sum(axis=1)

    # Keep the first column
    first_column = instance_count.iloc[:, 0]

    # Concatenate the first column with the summed columns
    instance_count = pd.concat([first_column, summed_columns], axis=1)
    instance_count.columns.values[1] = 'Instance Count'
    instance_count_size = instance_count.shape[0]
    instance_count_error_time = []
    for i in range(instance_count_size):
        if instance_count.iloc[i,1] > 2 :
            instance_count_error_time.append(instance_count.iloc[i,0])
    return instance_count_error_time


def checkRequestCount(filename):
    """
    Request Count: 0.9 quantile as threshold
    每次threshold拿最近60分鐘的?
    假設從10:00開始,那就從9:00開始收集data
    """
    request_count = pd.read_csv(filename)
    request_count.iloc[:, 1:] = request_count.iloc[:, 1:].astype(int) 
    
    
    summed_columns = request_count.iloc[:, 1:].sum(axis=1)

    # Keep the first column
    first_column = request_count.iloc[:, 0]

    # Concatenate the first column with the summed columns
    request_count = pd.concat([first_column, summed_columns], axis=1)



    request_count.columns.values[1] = 'Request Count'
    request_count_size = request_count.shape[0]
    request_count_error_time = []
    for i in range(request_count_size):
        request_count_threshold = request_count.iloc[:,1].quantile(0.90)
        if request_count.iloc[i,1] > request_count_threshold:
            request_count_error_time.append(request_count.iloc[i,0])
    return request_count_error_time


def checkRequestLatency(filename):
    """
    Request Latency: 0.9 quantile as threshold
    先抓最近60分鐘的?
    """
    request_latency = pd.read_csv(filename)
    request_latency.columns.values[1] = 'Request Latency (ms)'
    request_latency.iloc[:, 1] = request_latency.iloc[:, 1].astype(float)  
    request_latency_size = request_latency.shape[0]
    request_latency_error_time = []
    for i in range(request_latency_size):
        request_latency_threshold = request_latency.iloc[:,1].quantile(0.90)
        if request_latency.iloc[i,1] > request_latency_threshold:
            request_latency_error_time.append(request_latency.iloc[i,0])
    return request_latency_error_time



def getClump(time_series):
    """
    getClump 把時間點變成大略時間範圍
    """
    time_series = list(time_series) 
    # Convert the time series strings to datetime objects
    time_series = [datetime.strptime(time,"%a %b %d %Y %H:%M:%S ") for time in time_series]
    
    # Define the gap tolerance (1-2 minutes)
    gap_tolerance = timedelta(minutes=2)
    
    # Initialize variables for clumps
    clumps = []
    current_clump = [time_series[0]]
    
    # Iterate through the time series and group them into clumps
    
    for i in range(1, len(time_series)):
        if time_series[i] - time_series[i-1] <= gap_tolerance:
            current_clump.append(time_series[i])
        else:
            clumps.append(current_clump)
            current_clump = [time_series[i]]
    
    # Append the last clump
    clumps.append(current_clump)
    
    # Convert clumps back to string representation
    clumps = [[time.strftime("%a %b %d %Y %H:%M:%S ") for time in clump] for clump in clumps]
    result = []
    # Print the resulting clumps
    for clump in clumps:
        if len(clump) > 1:
            clump=[clump[0]+' to '+clump[-1]]
        result.append(clump)
    return result


def getPrompt(cpu_utilization_file, memory_utilization_file, cloudrun_restart_file,
              instance_count_file, request_count_file, request_latency_file):
    """
    Get Prompt for LLM
    """
    cpu_utilization_error = checkCPUutilization(cpu_utilization_file)
    memory_utilization_error = checkMEMORYutilization(memory_utilization_file)
    cloudrun_restart_error = checkCloudRunReStart(cloudrun_restart_file)
    instance_count_error = checkInstanceCount(instance_count_file)
    request_count_error = checkRequestCount(request_count_file)
    request_latency_error = checkRequestLatency(request_latency_file)
    
    prompt = '''I am a system developer of TSMC Infrastructure employee, and i want to monitor the IT system on Google Cloud Platform,
to be specific, to monitor the metric and loggings obtained from Google CloudRun. 
The metric consists of several class, like:  Request Count, Request Latency, Instance Count, Container CPU Utilization, Container Memory Utilization, Container startup latency.
(And here are some explaination of them:
Request Count:
Description: This metric measures the total number of requests received by your service within a given time frame.
Importance: It helps in understanding the traffic pattern and volume your application is handling. Analyzing this metric can help in capacity planning and identifying peak usage times.
Request Latency:
Description: Request latency is the time it takes for your service to respond to a request. This is usually measured from the time a request is received until the response is sent back to the client.
Importance: It's a critical metric for assessing the user experience. High latency can lead to slow application performance, affecting user satisfaction. Monitoring latency can help in identifying performance bottlenecks.
Instance Count:
Description: This metric indicates the number of instances that are running at any given time. In Cloud Run, instances are scaled automatically based on the incoming request volume and the configurations set for maximum and minimum instances.
Importance: Monitoring the instance count helps in understanding how well your application scales with traffic and whether the auto-scaling configurations are appropriate for the workload.
Container CPU Utilization:
Description: This metric measures the percentage of allocated CPU resources being used by your container. It's a gauge of how much computational work your application is performing.
Importance: High CPU utilization could indicate that your application is CPU-bound or experiencing high traffic. Monitoring this can help in resource optimization and identifying when to upgrade to a higher CPU allocation.
Container Memory Utilization:
Description: Similar to CPU utilization, this metric measures the percentage of allocated memory resources being used by your container.
Importance: Memory utilization is crucial for identifying memory leaks or inefficient memory use. Consistently high memory usage might necessitate an increase in the allocated memory to prevent out-of-memory errors.
Container Startup Latency:
Description: This metric refers to the time it takes for a new container instance to start and be ready to serve requests. It includes the time taken to pull the container image, start the container, and initialize the application.
Importance: Monitoring startup latency is important for understanding the responsiveness of your service, especially under scaling events. High startup latencies can lead to delayed responses during traffic spikes.
),Beyond monitoring, i have also found several possible errors in the metrics for each class and marked the time when they happend, 
'''
    add_prompt = ''
    if cpu_utilization_error:
        add_prompt += ('There are errors about Container CPU utilization at '+str(getClump(cpu_utilization_error))+'.\n')
    
    if memory_utilization_error:
        add_prompt += ('There are errors about Container Memory utilization at '+str(getClump(memory_utilization_error))+'.\n')
    
    if cloudrun_restart_error:
        add_prompt += ('The CloundRun has re-started at '+str(cloudrun_restart_error)+'.\n')
    
    if instance_count_error:
        add_prompt += ('There are errors about Instance Count at '+str(getClump(instance_count_error))+'.\n')
    
    if request_count_error:
        add_prompt += ('There are errors about Request Count at '+str(getClump(request_count_error))+'.\n')
    
    if request_latency_error:
        add_prompt += ('There are errors about Request Latency at '+str(getClump(request_latency_error))+'.\n')
    
    if add_prompt:
        prompt += (add_prompt+'As a AI assistant, you have access to the data, and your job is to help me analyze the error information and provide me with recommendations of remediations')
    else:
        prompt += 'But no error was found.'
    return prompt

def interview(prompt: str):
    vertexai.init(project="tsmccareerhack2024-icsd-grp2",location="us-central1")
    parameters = {
        "temperature": 0.8,  # Temperature controls the degree of randomness in token selection.
        "max_output_tokens": 2048,  # (2048)Token limit determines the maximum amount of text output.
        "top_p": 0.8,  # (0.8)Tokens are selected from most probable to least until the sum of their probabilities equals the top_p value.
        "top_k": 20,  # (20)A top_k of 1 means the selected token is the most probable among all tokens.
    }

    model = TextGenerationModel.from_pretrained("text-bison@002")
    response = model.predict(
        prompt,
        **parameters,
    )
    #print(f"Response from Model: {response.text}")

    return response.text


def send_email(subject, body, to_email):
    # 邮件服务器的地址和端口
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    # 发件人的 Gmail 地址和密码
    sender_email = "zhenghan900513@gmail.com"
    sender_password = "ovbe nfdn ufmh nugr"

    # 收件人的邮箱地址
    recipient_email = to_email

    body_html = markdown2.markdown(body)

    # 构建邮件内容
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = subject
    body_content = MIMEText(body_html, "html")
    message.attach(body_content)

    # 使用 TLS 连接到 Gmail 邮件服务器
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()

        # 登录到 Gmail 邮件服务器
        server.login(sender_email, sender_password)

        # 发送邮件
        server.sendmail(sender_email, recipient_email, message.as_string())

    #print(f"Email sent to {recipient_email}")

# 切换到包含文件的目录
os.chdir('/home/icsd_user05_tsmc_hackathon_cloud/app/monitor/sample_data/ICSD Cloud Resource Training')
question = getPrompt('Container CPU Utilization.csv', 'Container Memory Utilization.csv', 'Container Startup Latency.csv', 'Instance Count.csv', 'Request Count.csv','Request Latency.csv')


text = interview(question)


send_email("alert", text, "sharon.lin.2001@gmail.com")

# 结束时间
end_time = time.time()

# 計算run time
run_time = end_time - start_＿time

print(f"run time : {run_time} s")

























