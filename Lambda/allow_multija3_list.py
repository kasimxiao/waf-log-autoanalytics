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
        query = cf.get('allow_multija3_list', 'query')
        
        # 执行OpenSearch查询
        result = opensearch_handler.execute_sql_query(query)
        if not result or len(result.get('datarows', [])) == 0:
            return '无可疑JA3指纹需要处理'
            
        # 获取当前规则组
        rule_group = waf_handler.get_rule_group()
        if not rule_group:
            return 'WAF规则组获取失败'
            
        # 提取当前规则
        current_rules = rule_group['Rules']
        current_ja3s = set()
        for rule in current_rules:
            if rule.get('Statement', {}).get('ByteMatchStatement', {}).get('SearchString'):
                current_ja3s.add(rule['Statement']['ByteMatchStatement']['SearchString'])
        
        # 处理新的JA3指纹
        new_rules = []
        message = '检测到以下JA3指纹异常:\n'
        
        for row in result['datarows']:
            ja3 = row[0]  # ja3Fingerprint
            ip_count = row[1]  # count of distinct IPs
            
            if ja3 not in current_ja3s:
                # 创建新规则
                rule = {
                    'Name': f'JA3_{ja3[:8]}',
                    'Priority': len(current_rules) + len(new_rules) + 1,
                    'Statement': {
                        'ByteMatchStatement': {
                            'FieldToMatch': {
                                'SingleHeader': {
                                    'Name': 'ja3-fingerprint'
                                }
                            },
                            'PositionalConstraint': 'EXACTLY',
                            'SearchString': ja3,
                            'TextTransformations': [{
                                'Priority': 1,
                                'Type': 'NONE'
                            }]
                        }
                    },
                    'Action': {
                        'Block': {}
                    },
                    'VisibilityConfig': {
                        'SampledRequestsEnabled': True,
                        'CloudWatchMetricsEnabled': True,
                        'MetricName': f'JA3_{ja3[:8]}'
                    }
                }
                new_rules.append(rule)
                message += f'JA3: {ja3}, 使用IP数: {ip_count}\n'
                
                # 记录到MySQL
                record = {
                    'ja3': ja3,
                    'ip_count': ip_count,
                    'status': 'BLOCKED'
                }
                mysql_handler.insert_record('ja3_records', record)
        
        if not new_rules:
            return '无新的可疑JA3指纹需要处理'
            
        # 更新规则组
        all_rules = current_rules + new_rules
        if waf_handler.update_rule_group(all_rules, rule_group['LockToken']):
            return message
        else:
            return 'WAF规则组更新失败'
            
    except Exception as e:
        print(f"Error in task_execute: {e}")
        return f'任务执行出错: {str(e)}'