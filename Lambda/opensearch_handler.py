from opensearchpy import OpenSearch,RequestsHttpConnection,helpers
import configparser
import re

# 读取配置文件 
def read_config():
    cf = configparser.ConfigParser()
    cf.read('config.ini', encoding="utf-8")  # 读取config.ini
    return cf

def get_table_name():
    """
    从配置文件获取表名
    """
    return cf.get('aos-config', 'table_name')

def replace_variables(query):
    """
    替换查询中的变量
    """
    table_name = get_table_name()
    return query.replace('{table_name}', table_name)

def querySQL(query):
    """
    执行SQL查询
    """
    query = replace_variables(query)
    response = es.transport.perform_request(
        'POST',
        '/_plugins/_sql',
        body={'query': query}
    )
    return response['datarows']
    
def queryDSL(query, index=None):
    """
    执行DSL查询
    如果没有指定index,使用配置文件中的table_name
    """
    if not index:
        index = get_table_name()
    
    response = es.search(
        body=query,
        index=index
    )
    return response

cf = read_config()
cf_tag = 'aos-config'
host = cf.get(cf_tag, 'host')
service = cf.get(cf_tag, 'service')
credentials = (cf.get(cf_tag, 'user'), cf.get(cf_tag, 'pwd'))

# Create the client.
es = OpenSearch(
    hosts = [{'host': host, 'port': 443}],
    http_auth = credentials,
    use_ssl = True,
    verify_certs = True,
    http_compress = True, # enables gzip compression for request bodies
    connection_class = RequestsHttpConnection,
    timeout = 30
)
