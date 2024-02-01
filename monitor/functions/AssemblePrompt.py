#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 25 14:33:03 2024

@author: hanworld
"""

def assemblePrompts(metric_prompt, logging_prompt): 
    if (not metric_prompt) and (not logging_prompt):
        print("沒有發現異常")
        return False
    
    assemble_prompt = '''I am a system developer, and i want to monitor the system on Google Cloud Platform,
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
)
Logging in the context of a system refers to the process of recording events, actions, and operations that occur within the system. This involves generating and storing log messages or entries, which typically include details such as timestamps, event types, severity levels, messages describing the event, and possibly the component or module where the event occurred. 
Logs serve as a chronological record of events and are crucial for various aspects of system management and analysis.
(Purposes and Importance of Logging:
Debugging: Logs provide developers with a detailed context of what the system was doing at a given time, making it easier to identify and fix bugs or issues.
Monitoring: System administrators and operations teams monitor logs to keep track of the system's health and performance in real-time, enabling them to detect and respond to issues promptly.
Security: Logging is vital for security analysis, allowing security teams to detect and investigate unauthorized access attempts, security breaches, and other potential vulnerabilities.
Compliance: In many industries, regulations require logging certain types of data and events for compliance purposes, ensuring that the system adheres to legal and regulatory standards.
Audit Trails: Logs provide an audit trail that can be used to understand the sequence of events leading up to an issue, making it possible to establish accountability and trace back user actions.
Performance Analysis: By analyzing logs, it's possible to identify performance bottlenecks and trends over time, aiding in capacity planning and optimization efforts.
Types of Logs:
Application Logs: Record events related to the application's operations, such as user actions, system errors, and transactions.
System Logs: Capture events at the operating system level, including system errors, boot processes, and hardware status.
Security Logs: Focus on security-related events, like login attempts, access control violations, and network security alerts.
Audit Logs: Track specific user activities and changes within the system to provide a detailed audit trail.
Logging Best Practices:
Consistency: Use a consistent format and level of detail across log messages to make them easier to read and analyze.
Severity Levels: Classify log messages by severity (e.g., DEBUG, INFO, WARN, ERROR) to help filter and prioritize them during analysis.
Retention Policies: Define policies for log rotation and retention to manage storage while ensuring that logs are available for a sufficient period for analysis and compliance.
Security: Protect log data from unauthorized access and tampering, especially logs containing sensitive information.
Effective logging is a foundational element of system development and operations, providing visibility into the system's behavior and history, which is essential for maintaining operational reliability, security, and compliance.)
And here are some labeled error logging type for you to take consider of: 
SERVICE_UNAVAILABLE_ERROR_503:
This error indicates that the server is currently unable to handle the request due to temporary overloading or maintenance of the server. The "503 Service Unavailable" status code is part of the HTTP standard response codes. It suggests that the service should be available again after some time.
NO_INSTANCE_AVAILABLE_ERROR_500:
This typically indicates an internal server error (represented by the "500 Internal Server Error" HTTP status code) where the service couldn't fulfill the request because no instances of the application or service were available to process the request. This might be due to configuration issues, scaling problems, or internal failures.
INSTANCE_START_FAILED_ERROR:
This error suggests that the system attempted to launch a new instance of a service or application, but the operation failed. This could be due to misconfiguration, insufficient resources, or underlying issues with the platform or infrastructure.
TOO_MANY_CLIENTS_ERROR:
This error occurs when too many simultaneous connections or requests are made to the server, exceeding its capacity to handle them. This might indicate a need for better scaling, rate limiting, or addressing a potential denial of service (DoS) attack.
MemoryLimitParsingError:
This error indicates a problem related to memory allocation or limits, possibly due to an application trying to use more memory than is allocated or available. It could also be triggered by issues in parsing configuration related to memory limits.
tcp-probe-failure:
This log message usually comes from health checks or monitoring systems that use TCP probes to determine the availability and health of services. A "tcp-probe-failure" indicates that a TCP connection attempt to a service failed, suggesting the service might be down, unreachable, or experiencing network issues.)
Beyond monitoring, i am also trying to find errors in metrics and loggings.
As a AI assistant, you have access to the data, and your job is combine both knowledge of metrics and loggings to help me answer the follow questions: 
    '''
    if metric_prompt and (not logging_prompt):
        assemble_prompt += ('I have found errors in metrics,' + metric_prompt)
    elif (not metric_prompt) and logging_prompt:
        assemble_prompt += ('I have found errors in loggings,' + logging_prompt)
    else:
        assemble_prompt += ('I have found errors in both metrics and loggings,' + metric_prompt + logging_prompt
                            + ',combine both error in metrics and error in loggings, ')
    assemble_prompt += 'analyze the error inforations and provide me with recommendations for remediation.'
    return assemble_prompt