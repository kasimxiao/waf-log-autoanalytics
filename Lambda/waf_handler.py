import boto3
import configparser
from datetime import datetime

# 读取配置文件 
def read_config():
    cf = configparser.ConfigParser()
    cf.read('config.ini', encoding="utf-8")  
    return cf

def get_waf_ip_set():
    """AWS WAF IP集"""
    try:
        # 初始化WAF客户端
        response = waf_client.get_ip_set(
            Name=ipset_name,
            Scope=ipset_region,
            Id=ipset_id
        )
        return response
    except Exception as e:
        print(f"获取waf ip set 错误: {str(e)}")
        raise

def update_waf_ip_set(addresses):
    """更新AWS WAF IP集"""
    try:
        waf_client.update_ip_set(
            Name=ipset_name,
            Scope=ipset_region,
            Id=ipset_id,
            Addresses=addresses,
            LockToken=get_waf_ip_set()['LockToken']
        )
        return True
    except Exception as e:
        print(f"更新 waf ip set 错误错误: {str(e)}")
        raise


def get_waf_rule_group():
    """AWS WAF IP集"""
    try:
        # 初始化WAF客户端
        response = waf_client.get_rule_group(
            Name=group_name,
            Scope=ipset_region,
            Id=group_id
        )
        return response
    except Exception as e:
        print(f"获取waf ip set 错误: {str(e)}")
        raise

#新增，保存最近10条
def add_rule_to_group(ja3_fingerprints):
    try:
        rule_list = []
        current_rule_group = get_waf_rule_group()
        existing_rules = current_rule_group['RuleGroup']['Rules']
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        rule_name = f'ja3_{timestamp}'
       # 创建 JA3 指纹匹配语句
        ja3_statements = []
        for ja3 in ja3_fingerprints:
            ja3_statements.append({
                'ByteMatchStatement': {
                    'SearchString': ja3,
                    'FieldToMatch':{
                        'JA3Fingerprint':{
                            'FallbackBehavior': 'MATCH'
                        }
                    },
                    'TextTransformations':[
                        {
                            'Priority': 0,
                            'Type': 'NONE'
                        }
                    ],
                    'PositionalConstraint': 'EXACTLY'
                }
            })

        # 创建新规则
        if len(ja3_fingerprints) == 1:
            statement = ja3_statements[0]
        else:
            statement = {
                'OrStatement': {
                    'Statements': ja3_statements
                }
            }
        new_rule = [{
            'Name': rule_name,
            'Priority': 0,
            'Statement': statement,
            'Action': {
                'Block': {}
            },
            'VisibilityConfig': {
                'SampledRequestsEnabled': True,
                'CloudWatchMetricsEnabled': True,
                'MetricName': f'{rule_name}-metric'
            }
        }]
        
        #该group ja3只保留最新10条，并按最新优先级最高重新排序
        priority = 1
        rules_result = []
        for i in existing_rules[:3]:
            i['Priority'] = priority
            rules_result.append(i)
            priority = priority+1


        # 将新规则添加到现有规则列表
        rules_result.append(new_rule[0])

        print(rules_result)
        # 更新 rule group
        response = waf_client.update_rule_group(
            Name=group_name,
            Scope=ipset_region,
            Id=group_id,
            Rules=rules_result,
            LockToken=current_rule_group['LockToken'],
            VisibilityConfig={
                'SampledRequestsEnabled': True,
                'CloudWatchMetricsEnabled': True,
                'MetricName': 'ja3'
            },
            Description='Updated rule group with JA3 fingerprint rule'
        )
        
        print(f"Successfully added JA3 rule '{rule_name}' to rule group")
        return True
        
    except Exception as e:
        print(f"添加规则时发生错误: {str(e)}")
        raise

#更新只保存汇总后一个rules
def update_rule_to_group(ja3_fingerprints):
    try:
        rule_list = []
        current_rule_group = get_waf_rule_group()
        existing_rules = current_rule_group['RuleGroup']['Rules']
        priority_num = 0
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        rule_name = f'ja3_{timestamp}'
       # 创建 JA3 指纹匹配语句
        ja3_statements = []
        for ja3 in ja3_fingerprints:
            ja3_statements.append({
                'ByteMatchStatement': {
                    'SearchString': ja3,
                    'FieldToMatch':{
                        'JA3Fingerprint':{
                            'FallbackBehavior': 'MATCH'
                        }
                    },
                    'TextTransformations':[
                        {
                            'Priority': 0,
                            'Type': 'NONE'
                        }
                    ],
                    'PositionalConstraint': 'EXACTLY'
                }
            })

        # 创建新规则
        if len(ja3_statements) == 1:
            statement = ja3_statements[0]
        else:
            statement = {
                'OrStatement': {
                    'Statements': ja3_statements
                }
            }

        new_rule = [{
            'Name': rule_name,
            'Priority': priority_num,
            'Statement': statement,
            'Action': {
                'Block': {}
            },
            'VisibilityConfig': {
                'SampledRequestsEnabled': True,
                'CloudWatchMetricsEnabled': True,
                'MetricName': f'{rule_name}-metric'
            }
        }]
    
        # 更新 rule group
        response = waf_client.update_rule_group(
            Name=group_name,
            Scope=ipset_region,
            Id=group_id,
            Rules=new_rule,
            LockToken=current_rule_group['LockToken'],
            VisibilityConfig={
                'SampledRequestsEnabled': True,
                'CloudWatchMetricsEnabled': True,
                'MetricName': 'ja3'
            },
            Description='Updated rule group with JA3 fingerprint rule'
        )
        
        print(f"Successfully added JA3 rule '{rule_name}' to rule group")
        return True
        
    except Exception as e:
        print(f"添加规则时发生错误: {str(e)}")
        raise

cf = read_config()
cf_tag = 'waf-config'
ipset_name = cf.get(cf_tag, 'ipset_name')
ipset_region = cf.get(cf_tag, 'ipset_region')
ipset_id = cf.get(cf_tag, 'ipset_id')
group_name = cf.get(cf_tag, 'group_name')
group_id = cf.get(cf_tag, 'group_id')

waf_client = boto3.client('wafv2',region_name='us-east-1')
