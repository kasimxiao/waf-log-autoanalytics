import json
import boto3
from datetime import datetime, timedelta
import time
import block_rules_list
import allow_multija3_list
import allow_iprate_list
import configparser
import ast

# 读取配置文件 
def read_config():
    cf = configparser.ConfigParser()
    cf.read('config.ini', encoding="utf-8")  # 读取config.ini
    return cf

def send_sns_message(topic_arn, message):
    try:
        # 发送消息到 SNS 主题
        response = sns_client.publish(
            TopicArn=topic_arn,
            Message=message
        )
        print(f"Message sent! Message ID: {response['MessageId']}")
    except Exception as e:
        print(f"An error occurred: {e}")


sns_client = boto3.client(service_name='sns')
cf = read_config()
topic_arn = cf.get('sns', 'topic_arn')
dashboard_url = cf.get('dashboard', 'dashboard_url')

def lambda_handler(event, context):
    message = ''
    #被block后仍然高频访问的IP，写入black ip set，可配置XX天后自动移除
    message = block_rules_list.task_excute()

    #同一个JA3，不同的ip使用，将ja3加入waf group rules，保留最近的XX条
    message = f'{message}\n\n{allow_multija3_list.task_excute()}'

    #ALLOW请求中，针对高频请求TOP IP，获取请求明细，llm进行分析识别
    message = f'{message}\n\n{allow_iprate_list.task_excute()}'

    if len(message.strip())>0:
        message = f'{message}\n详情可见url\t{dashboard_url}'
        send_sns_message(topic_arn, message)
        
    return {
        'statusCode': 200,
    }

