import opensearch_handler
import waf_handler
import mysql_handler
import configparser
import json

# 读取配置文件
def read_config():
    cf = configparser.ConfigParser()
    cf.read('config.ini', encoding="utf-8")
    return cf

cf = read_config()

def task_excute():
    try:
        # 获取配置参数
        query = cf.get('block_rulues_list', 'query')
        
        # 执行OpenSearch查询
        result = opensearch_handler.execute_sql_query(query)
        if not result or len(result.get('datarows', [])) == 0:
            return '无高频访问IP需要处理'
            
        # 获取当前IP集合
        ipset = waf_handler.get_ipset()
        if not ipset:
            return 'WAF IP集合获取失败'
            
        # 提取当前IP地址列表
        current_ips = set(ipset['Addresses'])
        
        # 处理新的IP地址
        new_ips = set()
        message = '检测到以下IP需要加入黑名单:\n'
        
        for row in result['datarows']:
            ip = row[0]  # clientIp
            ja3 = row[1]  # ja3Fingerprint
            country = row[2]  # country
            rule_id = row[3]  # terminatingRuleId
            location = row[4]  # location
            count = row[5]  # count
            
            if ip not in current_ips:
                new_ips.add(ip)
                message += f'IP: {ip}, 国家: {country}, 命中规则: {rule_id}, 位置: {location}, 次数: {count}\n'
                
                # 记录到MySQL
                record = {
                    'ip': ip,
                    'ja3': ja3,
                    'country': country,
                    'rule_id': rule_id,
                    'location': location,
                    'count': count,
                    'status': 'BLOCKED'
                }
                mysql_handler.insert_record('ip_records', record)
        
        if not new_ips:
            return '无新的高频访问IP需要处理'
            
        # 更新IP集合
        all_ips = list(current_ips | new_ips)
        if waf_handler.update_ipset(all_ips, ipset['LockToken']):
            return message
        else:
            return 'WAF IP集合更新失败'
            
    except Exception as e:
        print(f"Error in task_execute: {e}")
        return f'任务执行出错: {str(e)}'