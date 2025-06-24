from opensearch_handler import querySQL, queryDSL, get_table_name
import configparser
import waf_handler
import ipaddress

from mysql_handler import (
    insert_block_history, 
    insert_new_blockips,
    update_expire_blockips,
    get_allblock_ips,
    close_mysql_connection
)
from waf_handler import update_waf_ip_set

# 读取配置文件 
def read_config():
    cf = configparser.ConfigParser()
    cf.read('config.ini', encoding="utf-8")  # 读取config.ini
    return cf

def query_aos(task_name):
    """
    执行OpenSearch查询
    使用配置文件中的查询语句和类型
    """
    cf = read_config()
    query_string = cf.get(task_name, 'query')
    query_type = cf.get(task_name, 'type')

    if query_type == 'SQL':
        result = querySQL(query_string)
    else:
        # DSL查询使用配置的table_name作为index
        result = queryDSL(query_string)

    return result

def task_excute():
    task_name = 'block_rulues_list'
    message = ''
    #获取block后仍然大量请求的ip
    block_result = query_aos(task_name)

    ip_string = ''
    for i in block_result:
        #log写入mysql block_count_history表
        insert_block_history(i)
        #ip写入/更新 mysql block_ip_set表
        insert_new_blockips(i[0],i[1])
        ip_string = f'{ip_string}\n{i[0]}\t{i[3]}'

    #更新waf block ip
    update_expire_blockips()

    #获取mysql block ip 3天内的被阻止的 ip
    blockip_list = get_allblock_ips()

    #更新waf ip set
    ip_list = []
    for i in blockip_list:
        ip_list.append(i[0]+'/32')
    print(f'blockip:{ip_list}')
    update_waf_ip_set(ip_list)
    
    if len(ip_string) > 0:
        message = f'以下IP在Block后仍然产生大量请求，将被接入更名单池进行封禁{ip_string}\n'

    return message

