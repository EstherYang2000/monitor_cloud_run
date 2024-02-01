#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from string import Template
from pathlib import Path
from datetime import datetime
import markdown2
import pytz
def datetime_now():
    # Set the time zone to Taiwan
    taiwan_tz = pytz.timezone('Asia/Taipei')

    # Get the current time in UTC
    now_utc = datetime.now(pytz.utc)

    # Convert the current time to Taiwan's time zone
    now_taiwan = now_utc.astimezone(taiwan_tz)

    # Format the datetime as a string
    datetime_string = now_taiwan.strftime('%Y-%m-%d %H:%M:%S')
    return datetime_string
def send_email(time,subject, body, to_email,cpu_s,cpu_m):
    # 邮件服务器的地址和端口
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    # 发件人的 Gmail 地址和密码
    sender_email = "xxxxx@gmail.com"
    sender_password = "ovbe nfdn ufmh nugr"

    # 收件人的邮箱地址
    recipient_email = to_email
    html_template = Template(Path("/home/icsd_user05_tsmc_hackathon_cloud/app/monitor/data/email.html").read_text())

    # 构建邮件内容
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = subject
    move = "Scale up has been automatically performed to adjust the memory to 512Gb." 
    cost_move = "\n The cost will increase by $0.00000125 per second."
    move1 = "Scale up has been automatically performed to adjust the cpu to 2." 
    cost1 = "\n The cost will increase by $0.000024 per second."
    both = "Scale up has been automatically performed to adjust the cpu to 2 and the memory to 512Gb."
    cost_both = " \n The cost will increase by $0.000024 + $0.00000125 = $0.00002525 per second."
    #判斷是否有scale up
    # if cpu_s and cpu_m:
    #     # 邮件正文
    #     body_content = MIMEText(str(time)+"\n\n"+body, "plain" + both)
    # elif cpu_s:
    #     body_content = MIMEText(str(time)+"\n\n"+body, "plain" + move1)
    # elif cpu_m:
    #     body_content = MIMEText(str(time)+"\n\n"+body, "plain" + move)
    # else:
    #     body_content = MIMEText(str(time)+"\n\n"+body, "plain")
    # Determine the scale-up action
    scaling = ""
    cost = ""
    if cpu_s and cpu_m:
        scaling = f"\n\n{both}"
        cost = f"{cost_both}"
    elif cpu_s:
        scaling = f"\n\n{move1}"
        cost = f"{cost1}"
    elif cpu_m:
        scaling = f"\n\n{move}"
        cost = f"{cost_move}"
    else:
        scaling = f""
        cost = ""
    
    # Replace the placeholder with your actual message
    datetime_string = datetime_now()
    if scaling == "":
        time = ""
    else:   
        time = f"Scaling Resource Time : {time}"
    body_html = markdown2.markdown(body)
    html_content = html_template.substitute({"time":datetime_string,"scalingtime":time,"scaling": scaling,"cost":cost,"suggestion":body_html})
    # Create a MIMEText object for the HTML content
    html_part = MIMEText(html_content, "html")
    message.attach(html_part)
    # 使用 TLS 连接到 Gmail 邮件服务器
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        # 登录到 Gmail 邮件服务器
        server.login(sender_email, sender_password)
        # 发送邮件
        server.sendmail(sender_email, recipient_email, message.as_string())

"""
# 示例用法
subject = "Test Email"
body = "This is a test email sent from Python."
to_email = "xxxxxxx"

send_email(subject, body, to_email)"""

send_email("20200127","alert", "This is a test email sent from Python.", "xxxxx@gmail.com",True,True)