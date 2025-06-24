from opensearch_handler import querySQL, queryDSL, get_table_name
import configparser
import json
from waf_handler import (
    add_rule_to_group,
    update_rule_to_group
)
from claude_handler import generate_message
from mysql_handler import (
    insert_exception_detail,
    get_ja3_exception_list
)
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
    print(task_name)
    if task_name == 'allow_multija3_detail':
        # query_json = json.loads(query_string)
        # for item in query_json['query']['bool']['filter']:
        #     if 'terms' in item and 'ja3Fingerprint.keyword' in item['terms']:
        #         item['terms']['ja3Fingerprint.keyword'] = parameters
        #         break
        
        ja3_list = '("' + '", "'.join(parameters) + '")'
        query_string = query_string.replace('{ja3_list}', ja3_list)

    if query_type == 'SQL':
        result = querySQL(query_string)
    else:
        # DSL查询使用配置的table_name
        result = queryDSL(query_string)

    return result

def process_dsl_results(response):
    # results = []
    # hits = response['hits']['hits']
    # for i in hits:
    #     inner_hits = i['inner_hits']['by_ja3']['hits']['hits']
    #     for hit in  inner_hits:
    #         detail_list = []
    #         detail_list.append(hit['_source']['ja3Fingerprint'])
    #         detail_list.append(hit['_source']['httpRequest']['clientIp'])
    #         detail_list.append(hit['_source']['httpRequest']['headers'])
    #         detail_list.append(hit['_source']['httpRequest']['args'])
    #         detail_list.append(hit['_source']['httpRequest']['uri'])
    #         results.append(detail_list)
    
    return response

def extract_array(text):
    # 使用正则表式匹配 '[' 和 ']' 之间的内容（包括嵌套的方括号）
    pattern = r'\[.*\]'
    match = re.search(pattern, text, re.DOTALL)  # re.DOTALL 允许匹配换行符
    if match:
        return match.group()
    return ''

def task_excute():
    cf = read_config()
    task_name = 'allow_multija3_list'
    message = ''
    #获取相同JA3 覆盖了多个IP
    ja3_result = query_aos(task_name)
    
    if len(ja3_result) == 0:
        return message

    task_name = 'allow_multija3_detail'
    system_prompt = cf.get(task_name, 'system_prompt')
    user_prompt = cf.get(task_name, 'user_prompt')
    ja3_list = []
    for i in ja3_result:
        ja3_list.append(i[0])

    #print(f'JA3list:{ja3_list}')
    detail_result = query_aos(task_name,ja3_list)
    #print(f'detail_result:{detail_result}')
    #测试代码
    # with open('test/ja3.json') as json_data:
    #     detail_result = json.load(json_data)
    
    #转化为数组，减小token input
    detail_list = process_dsl_results(detail_result)
    user_prompt=f'{user_prompt}/n{detail_list}'
    response = generate_message(system_prompt,user_prompt,'检测')

    if '检测正常' in f'检测{response}':
        return message
    
    # print(f'检测{response}')

    exception_result = extract_array(response)
    exception_list = eval(exception_result)

    seen = set()  # 用于去重
    # 先执行所有的数据库插入
    for i in exception_list:
        i = list(i)
        print(i)
        i[1:1] = ['ja3', '']
        insert_exception_detail(i)
        seen.add(f"{i[0]}\t{i[1]}\t{i[2]}\t{i[3]}\t{i[4]}")  # 将需要的字符串组合添加到集合中

    # 将去重后的结果拼接成最终字符串
    ja3_string = '\n'.join(seen)

    if len(ja3_string) > 0:
        message = f'以下JA3同时多个IP使用，经分析判定为恶意请求，将被封禁\n{ja3_string}\n'

    #新增 waf group
    # add_rule_to_group(ja3_list)
        
    # 获取XX时间段内异常ja3
    ja3_result = get_ja3_exception_list()
    ja3_list =  [item[0] for item in ja3_result]
    print(f'ja3_list:{ja3_list}')
    #更新 waf group
    # add_rule_to_group(ja3_list)
    update_rule_to_group(ja3_list)
    return message

