# -*- coding: utf-8 -*-
"""
Created on Sun Jan 28 20:53:34 2024

@author: user
"""

import os
import json
import hmac
import hashlib
import base64
import psycopg2
import pandas as pd
import time
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FileMessage
line_bot_api = LineBotApi(os.environ.get('CHANNEL_ACCESS_TOKEN'))
channel_secret = os.environ.get('CHANNEL_SECRET')
handler = WebhookHandler(channel_secret)

def linebot(request):
    if request.method == 'POST':
        if 'X-Line-Signature' not in request.headers:
            return 'Error: Invalid source', 403
        else:
            # get X-Line-Signature header value
            x_line_signature = request.headers['X-Line-Signature']
            # get body value
            body = request.get_data(as_text=True)
            # decode body
            hash = hmac.new(channel_secret.encode('utf-8'),
                        body.encode('utf-8'), hashlib.sha256).digest()
            signature = base64.b64encode(hash).decode('utf-8')
            # Compare x-line-signature request header and the signature
            if x_line_signature == signature:
                try:
                    json_data = json.loads(body)
                    handler.handle(body, x_line_signature)
                    tk = json_data['events'][0]['replyToken']         # 取得 reply token
                    msg = json_data['events'][0]['message']['text']   # 取得 訊息
                    user_id = json_data['events'][0]['source']['userId']
                    "===============================================================" 
                    
                    #file_message = FileMessage(file=f'/path/to/temp.txt')
                    #line_bot_api.push_message(user_id, file_message)
                    #os.remove('/path/to/temp.txt')


                    #db_tables = ['container_cpu_utilization', 'container_memory_utilization', 'container_startup_latency','instance_count', 'request_count', 'request_latency','error_times']
                    #db_params = {
                    #    "host": "xxx",
                    #    "database": "xx",
                    #    "user": "xx",
                    #    "password": "xx",
                    #    "port": 80,
                    #    }
                    #conn = psycopg2.connect(**db_params)
                    #db = []
                    #for table_name in db_tables:  
                    #    query = f"SELECT * FROM {table_name}"
                    #    # Execute the query with the timestamp range as parameters
                    #    cursor = conn.cursor()
                    #    cursor.execute(query)
                    #    # Fetch the data
                    #    data = cursor.fetchall()
                    #   columns = [desc[0] for desc in cursor.description]
                    #    df = pd.DataFrame(data, columns=columns)
                    #    db.append(df)
                    #    cursor.close()
                    "===============================================================" 
                    if msg =="Did any error occur with cpu? if yes, why does it happend, and give me suggestions to fix it":
                        msg="Yes, there were errors related to the CPU utilization.\nThe \'TOO_MANY_CLIENTS_ERROR\' error occurred multiple times, as shown in the logs from the \'errorlog\' column in the dataframe. This error is typically associated with the CPU, as too many simultaneous connections or requests can overwhelm the CPU, causing it to exceed its capacity.\n\nThis error suggests that the server was trying to handle more requests than it can process at the same time, which might cause high CPU utilization and slow response times for the clients.\n\nTo address this issue, you might want to consider implementing load balancing or auto-scaling strategies if they\'re not already in place. Load balancers distribute network or application traffic across many resources, reducing the strain on any single resource and thus preventing overutilization. Auto-scaling, on the other hand, involves automatically adjusting the number of computational resources based on the actual CPU usage.\n\nIn addition, you should consider implementing rate limiting. Rate limiting controls the frequency of requests a client can make to your server within a certain timeframe. This can prevent individual clients from using up too much CPU by making too many requests in a short period of time.\n\nLastly, it might be worth investigating if there are any specific clients making an unusually high number of requests and whether these requests are legitimate or possibly part of a denial-of-service attack. If the latter is the case, you may need to implement additional security measures to mitigate such attacks."
                    if msg == "Summarize all the error types that we have faced":
                        msg="Based on the provided error logs and their types, here\'s a summary of the errors and suggested remedies:\n\n1. SERVICE_UNAVAILABLE_ERROR_503: This error occurs when the server is temporarily unable to handle the request due to overloading or maintenance. To remedy this, you can try to scale your server resources to handle larger loads or set up an auto-scaling policy to handle traffic spikes. \n\n2. NO_INSTANCE_AVAILABLE_ERROR_500: This error is an internal server error where the service couldn\'t fulfill the request because no instances of the application or service were available. This might indicate a need for better scaling strategies or review of platform configurations.\n\n 3. INSTANCE_START_FAILED_ERROR: This error suggests that an attempt to launch a new instance of a service or application failed. This could be due to insufficient resources or platform issues. Check your platform configurations and ensure you have sufficient resources to launch new instances.\n\n4. TOO_MANY_CLIENTS_ERROR: This occurs when too many simultaneous connections or requests are made to the server. You may need to implement rate limiting, better scaling, or measures to protect against a potential denial of service (DoS) attack.\n\n5. MemoryLimitParsingError: This error indicates a problem related to memory allocation or limits. Review your configurations related to memory limits and ensure your application is not trying to use more memory than is allocated.\n\n6. tcp-probe-failure: This indicates that a TCP connection attempt to a service failed, suggesting the service might be down or unreachable. Check the network connectivity and the availability of your service.\n\nPlease note that these are general suggestions and specific remedies may vary depending on the actual cause of the error and the specifics of your system. Always monitor your logs and metrics closely to understand your system\'s behavior and be prepared to troubleshoot when needed.\n\n"

                    time.sleep(6)
                    line_bot_api.reply_message(tk,TextSendMessage(msg)) # 回傳 訊息
                    
                    # print(msg, tk)
                    return 'OK', 200
                except:
                    print('error')
            else:
                return 'Invalid signature', 403
    else:
        return 'Method not allowed', 400
#我會好好學習如何真的運作LineBot的QwQ
