import boto3
import configparser

# 读取配置文件
def read_config():
    cf = configparser.ConfigParser()
    cf.read('config.ini', encoding="utf-8")
    return cf

cf = read_config()

# 获取配置参数
ipset_name = cf.get('waf-config', 'ipset_name')
ipset_region = cf.get('waf-config', 'ipset_region')
ipset_id = cf.get('waf-config', 'ipset_id')
group_name = cf.get('waf-config', 'group_name')
group_id = cf.get('waf-config', 'group_id')

# 初始化WAF客户端
wafv2_client = boto3.client('wafv2')

def get_ipset():
    try:
        response = wafv2_client.get_ip_set(
            Name=ipset_name,
            Scope=ipset_region,
            Id=ipset_id
        )
        return response['IPSet']
    except Exception as e:
        print(f"Error getting IP set: {e}")
        return None

def update_ipset(addresses, lock_token):
    try:
        response = wafv2_client.update_ip_set(
            Name=ipset_name,
            Scope=ipset_region,
            Id=ipset_id,
            Addresses=addresses,
            LockToken=lock_token
        )
        return True
    except Exception as e:
        print(f"Error updating IP set: {e}")
        return False

def get_rule_group():
    try:
        response = wafv2_client.get_rule_group(
            Name=group_name,
            Scope=ipset_region,
            Id=group_id
        )
        return response['RuleGroup']
    except Exception as e:
        print(f"Error getting rule group: {e}")
        return None

def update_rule_group(rules, lock_token):
    try:
        response = wafv2_client.update_rule_group(
            Name=group_name,
            Scope=ipset_region,
            Id=group_id,
            Rules=rules,
            LockToken=lock_token
        )
        return True
    except Exception as e:
        print(f"Error updating rule group: {e}")
        return False