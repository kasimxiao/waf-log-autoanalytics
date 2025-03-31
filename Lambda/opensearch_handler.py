import boto3
import requests
from requests.auth import HTTPBasicAuth
import configparser
import json

# 读取配置文件
def read_config():
    cf = configparser.ConfigParser()
    cf.read('config.ini', encoding="utf-8")
    return cf

cf = read_config()

# 获取配置参数
host = cf.get('aos-config', 'host')
user = cf.get('aos-config', 'user')
pwd = cf.get('aos-config', 'pwd')
table_name = cf.get('aos-config', 'table_name')

def execute_sql_query(query):
    try:
        # 替换变量
        query = query.replace('${table_name}', table_name)
        
        # 构建请求URL和数据
        url = f'https://{host}/_plugins/_sql'
        data = {
            'query': query
        }
        
        # 发送请求
        response = requests.post(
            url,
            auth=HTTPBasicAuth(user, pwd),
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        
        # 检查响应
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error executing SQL query: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error in execute_sql_query: {e}")
        return None

def execute_dsl_query(index, query):
    try:
        # 替换变量
        index = index.replace('${table_name}', table_name)
        
        # 构建请求URL
        url = f'https://{host}/{index}/_search'
        
        # 发送请求
        response = requests.post(
            url,
            auth=HTTPBasicAuth(user, pwd),
            json=query,
            headers={'Content-Type': 'application/json'}
        )
        
        # 检查响应
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error executing DSL query: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error in execute_dsl_query: {e}")
        return None