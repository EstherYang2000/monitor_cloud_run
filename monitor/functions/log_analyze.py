# -*- coding: utf-8 -*-
"""
Created on Wed Jan 24 23:43:18 2024

@author: user
"""

import vertexai
import json
from vertexai import preview
import numpy as np
from vertexai.language_models import TextEmbeddingModel
import random


def cosine(V1,V2):
    V1 = np.array(V1)
    V2 = np.array(V2)
    cosine_similarity = np.dot(V1, V2) / (np.linalg.norm(V1) * np.linalg.norm(V2))
    return cosine_similarity 
    
def text_embedding(s) -> list:
    """Text embedding with a Large Language Model."""
    model = TextEmbeddingModel.from_pretrained("textembedding-gecko@003")
    embeddings = model.get_embeddings([s])
    for embedding in embeddings:
        vector = embedding.values
    return vector    
def process_data(data):
    for i in range(len(data)):
        data[i].pop('resource', None) 
        data[i].pop('logName', None)
    return data

def analyze_log(log, error_logs):
    log_vector = text_embedding(str(log))
    cosine_values = [cosine(r, log_vector) for r in error_logs]
    max_index = cosine_values.index(max(cosine_values))
    if any(value > 0.92 for value in cosine_values):
        return max_index
    else:
        return -1    
    
def read_error_log():
    input_file = '/home/icsd_user05_tsmc_hackathon_cloud/app/monitor/data/error_log.txt'
    error_log = []
    with open(input_file, 'r') as file:
        for line in file:
            vector = [float(x) for x in line.strip().split()]
            error_log.append(vector)
    return error_log
#===================================================================================================================
def analyze_main_ontime(log):
    log_data=[]
    for k in range(10):
        i=random.randint(0,len(log)-1)
        log_data.append(log[i])
    log_data = process_data(log_data)
    error_labels = ["SERVICE_UNAVAILABLE_ERROR_503", "NO_INSTANCE_AVAILABLE_ERROR_500",
                    "INSTANCE_START_FAILED_ERROR", "TOO_MANY_CLIENTS_ERROR"]
    error_log_example = read_error_log()
    error_log = []

    for i in range(len(log_data)):
        result = analyze_log(log_data[i], error_log_example)
        if result >= 0:
            max_index = result
            error_msg = f"{log_data[i]['timestamp']},{error_labels[max_index]}"
            error_log.append(error_msg)

    if error_log:
        return "For the logging part, there is some error like " + ",".join(error_log)
    else:
        return False
    


"""
data_output = {
                "time": log_data['timestamp'],
                "ID": log_data["insertId"],
                "logging": log_data,
                "error": error_labels[max_index]
            }
"""
        































