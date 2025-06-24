from opensearch_handler import querySQL, queryDSL, get_table_name
import configparser
import json
from waf_handler import update_waf_ip_set
from claude_handler import generate_message
from mysql_handler import insert_exception_detail
import ast
import re


# 读取配置文件 
def read_config():
    cf = configparser.ConfigParser()
    cf.read('config.ini', encoding="utf-8")  # 读取config.ini
    return cf

def query_aos(task_name, parameters=None):
    """
    执行OpenSearch查询
    使用配置文件中的查询语句和类型
    """
    cf = read_config()
    query_string = cf.get(task_name, 'query')
    query_type = cf.get(task_name, 'type')

    # 替换查询中的table_name变量
    table_name = get_table_name()
    query_string = query_string.replace('${table_name}', table_name)

    if task_name == 'allow_request_detail':
        query_json = json.loads(query_string)
        for item in query_json['query']['bool']['filter']:
            if 'terms' in item and 'httpRequest.clientIp' in item['terms']:
                item['terms']['httpRequest.clientIp'] = parameters
                break
        query_string = json.dumps(query_json, indent=2)

    if query_type == 'SQL':
        result = querySQL(query_string)
    else:
        # DSL查询使用配置的table_name
        result = queryDSL(query_string)

    return result

def process_dsl_results(response):
    results = []
    hits = response['hits']['hits']
    for hit in hits:
        detail_list = []
        detail_list.append(hit['_source']['httpRequest']['clientIp'])
        detail_list.append(hit['_source']['httpRequest']['headers'])
        detail_list.append(hit['_source']['httpRequest']['args'])
        detail_list.append(hit['_source']['httpRequest']['uri'])
        results.append(detail_list)
    return results

def extract_array(text):
    # 使用正则表式匹配 '[' 和 ']' 之间的内容（包括嵌套的方括号）
    pattern = r'\[.*\]'
    match = re.search(pattern, text, re.DOTALL)  # re.DOTALL 允许匹配换行符
    if match:
        return match.group()
    return ''

def task_excute():
    cf = read_config()
    task_name = 'allow_iprate_list'
    message = ''
    #获取高频请求的ip和ja3
    highrate_result = query_aos(task_name)
    ip_list = []
    for i in highrate_result:
        ip_list.append(i[0])

    # if len(highrate_result) == 0:
    #     return message

    task_name = 'allow_request_detail'
    system_prompt = cf.get(task_name, 'system_prompt')
    user_prompt = cf.get(task_name, 'user_prompt')
    detail_result = query_aos(task_name,ip_list)

    #测试代码
    with open('ip.json') as json_data:
        detail_result = json.load(json_data)
    
    #转化为数组，减小token input
    detail_list = process_dsl_results(detail_result)
    user_prompt=f'{user_prompt}/n{detail_result}'
    # user_message =  {"role": "user", "content": prompt}
    # assistant_message =  {"role": "assistant", "content": "检测"}
    # messages = [user_message,assistant_message]
    # response = generate_message(messages)

    response = generate_message(system_prompt,user_prompt,'检测')


    print(response)

    if '巡检正常' in f'巡检{response}':
        return message
        
    # exception_result = response.replace('异常','')
    exception_result = extract_array(response)
    print('exception_result')
    print(exception_result)

    exception_list = eval(exception_result)
    #写入数据库
    seen = set()  # 用于去重
    # 先执行所有的数据库插入
    for i in exception_list:
        i = list(i)
        i[1:1] = ['ip']
        insert_exception_detail(i)
        seen.add(f"{i[0]}\t{i[1]}\t{i[2]}\t{i[3]}\t{i[4]}")  # 将需要的字符串组合添加到集合中

    # 将去重后的结果拼接成最终字符串
    exception_string = '\n'.join(seen)
    if len(exception_string) > 0:
        message = f'以下IP存在高频请求，经分析疑似为恶意请求，请进行进一步分析\n{exception_string}\n'

    return message
