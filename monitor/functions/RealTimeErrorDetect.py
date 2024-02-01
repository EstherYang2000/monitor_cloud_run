#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import subprocess
from command import *
from mql_metric_time_range import *

def before(project_id='tsmccareerhack2024-icsd-grp2', service_name ='hedgedoc',
                 resource_type = 'cloud_run_revision'):
    """
    抓上一個小時的RequestCount和RequestLatency的值
    前十分鐘的memory和cpu
    """
    df_RC = metric_range(type_interval='minutes',number_interval=60,metric_="RequestCount")
    df_RL = metric_range(type_interval='minutes',number_interval=60,metric_="RequestLatency")
    df_cpu = metric_range(type_interval = 'minutes',number_interval=10,metric_="cpu")
    df_mem = metric_range(type_interval = 'minutes',number_interval=10,metric_="memory")
    return  df_RC, df_RL, df_cpu, df_mem
    #要再確認一下 
# before("tsmccareerhack2024-icsd-grp2","hedgedoc", "cloud_run_revision")

def checkCPUutilization(utilization0,utilization1):
    """
    Container CPU Utilization (%) > 1.01
    只會抓最近兩筆資料
    """
    cpu_utilization_threshold = 0.0101
    if utilization0 > cpu_utilization_threshold and utilization1 > cpu_utilization_threshold:
        return utilization1 #cpu utilization error
    return False #no cpu utilization error


def checkMEMORYutilization(utilization0,utilization1):
    """
    Container Memory Utilization (%) > 20
    只會抓最近兩筆資料
    """
    memory_utilization_threshold = 0.01
    if utilization0> memory_utilization_threshold and utilization1 > memory_utilization_threshold:
        return utilization1 #memory utilization error
    return False #no memory utilization error


def checkCloudRunReStart(restart):
    """
    Cloud run re-start
    只會抓最新的一筆資料
    """
    if restart>0:
        return restart #there is re-start
    return False #there is no re-start


def checkInstanceCount(InstanceCount):
    """
    Instance count > 2
    只會抓最新的一筆資料
    """ 
    if InstanceCount > 2 :
        return InstanceCount #there is instance count error
    return False #there is no instance count error


def checkRequestCount(new_RequestCount,df_RC):
    """
    Request Count: 0.9 quantile as threshold
    執行程式前抓進最近60分鐘的
    再抓入新的值，最後60筆進行比較
    """
    df_RC.loc[len(df_RC)]=new_RequestCount
    request_count_threshold = df_RC.iloc[-60:].quantile(0.90)
    if new_RequestCount > float(request_count_threshold):
        return new_RequestCount,df_RC #there is sign of request count surge
    return -1,df_RC #there is no sign of request count surge



def checkRequestLatency(new_RequestLatency,df_RL):
    """
    Request Latency: 0.9 quantile as threshold
    執行程式前抓進最近60分鐘的
    再抓入新的值，最後60筆進行比較
    """
    df_RL.loc[len(df_RL)]=new_RequestLatency
    request_latency_threshold = df_RL.iloc[-60:].quantile(0.90)
    if new_RequestLatency > float(request_latency_threshold):
        return new_RequestLatency,df_RL #there is sign of request count surge
    return -1,df_RL #there is no sign of request count surge

def scale_or_not(df_cpu, df_mem):
    # if df_cpu[-2] > 0.2 and df_cpu[-1] > 0.2:
    #     scale_up_cpu()
    #     cpu_s = True
    # else:
    #     cpu_s = False
    # scale_up_cpu()
    cpu_s = False
    # all_greater_than_threshold = all(value > 0.02 for value in df_cpu[-2:])
    # if all_greater_than_threshold:
    #     scale_up_cpu()
    #     cpu_s = True
    # else:
    #     cpu_s = False
    
    # if df_mem[-2] > 0.2 and df_mem[-1] > 0.2:
    #     scale_up_mem()
    #     cpu_m = True
    # else:
    #     cpu_m = False
    scale_up_mem()
    cpu_m = True
    # all_greater_than_threshold = all(value > 0.02 for value in df_mem[-2:])
    # if all_greater_than_threshold:
    #     scale_up_mem()
    #     cpu_m = True
    # else:
    #     cpu_m = False
    return cpu_s,cpu_m

def getPrompt(cpu_utilization0,memory_utilization0,
                restart,InstanceCount,new_RequestCount,new_RequestLatency,project_id='tsmccareerhack2024-icsd-grp2', service_name ='hedgedoc',
                 resource_type = 'cloud_run_revision'):
    """
    Get Prompt for LLM
    """
    df_RC, df_RL, df_cpu, df_mem = before()
    cpu_utilization_error = checkCPUutilization(df_cpu[0][len(df_cpu)-1], cpu_utilization0)
    memory_utilization_error = checkMEMORYutilization(df_mem[0][len(df_mem)-1], memory_utilization0)
    cloudrun_restart_error = checkCloudRunReStart(restart)
    instance_count_error = checkInstanceCount(InstanceCount)
    request_count_error,_ = checkRequestCount(new_RequestCount,df_RC)
    request_latency_error,_ = checkRequestLatency(new_RequestLatency,df_RL)
    
    #判斷有沒有要scale
    cpu_s,cpu_m = scale_or_not(df_cpu, df_mem)

    prompt = 'For the metrics part,\n'
    add_prompt = ''
    if cpu_utilization_error:
        add_prompt += ('There is an error about Container CPU utilization of '+str(cpu_utilization_error*100)+'%.\n')
    
    if memory_utilization_error:
        add_prompt += ('There is an error about Container Memory utilization of '+str(memory_utilization_error*100)+'%.\n')
    
    if cloudrun_restart_error:
        add_prompt += ('The CloundRun has re-started in a latency of '+str(cloudrun_restart_error)+'ms.\n')
    
    if instance_count_error:
        add_prompt += ('There is an error about Instance Count of '+str(instance_count_error)+'times.\n')
    
    if request_count_error!=-1:
        add_prompt += ('There is an error about Request Count of '+str(request_count_error)+'times.\n')
    
    if request_latency_error!=-1:
        add_prompt += ('There is an error about Request Latency of '+str(request_latency_error)+'ms.\n')
    
    if add_prompt:
        prompt += add_prompt
    else:
        prompt = False
        #prompt = '' 看是要直接傳空還是解釋沒問題
    return prompt,cpu_s,cpu_m
