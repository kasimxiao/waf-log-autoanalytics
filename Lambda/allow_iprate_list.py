import opensearch_handler
import claude_handler
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
        # 获取高频访问IP
        query = """
        SELECT httpRequest.clientIp, ja3Fingerprint, httpRequest.country, count(*) as cnt
        FROM ${table_name}
        WHERE action = 'ALLOW'
        AND timestamp >= date_sub(now(), interval 1 day)
        GROUP BY httpRequest.clientIp, ja3Fingerprint, httpRequest.country
        HAVING COUNT(*) > 1000
        ORDER by cnt Desc
        LIMIT 10
        """
        
        result = opensearch_handler.execute_sql_query(query)
        if not result or len(result.get('datarows', [])) == 0:
            return '无高频访问IP需要分析'
            
        message = '检测到以下IP访问频率异常:\n'
        
        for row in result['datarows']:
            ip = row[0]  # clientIp
            ja3 = row[1]  # ja3Fingerprint
            country = row[2]  # country
            count = row[3]  # count
            
            # 获取详细请求信息
            detail_query = f"""
            SELECT timestamp, httpRequest.uri, httpRequest.headers, httpRequest.args
            FROM ${{table_name}}
            WHERE httpRequest.clientIp = '{ip}'
            AND timestamp >= date_sub(now(), interval 1 day)
            ORDER BY timestamp DESC
            LIMIT 50
            """
            
            detail_result = opensearch_handler.execute_sql_query(detail_query)
            if not detail_result or len(detail_result.get('datarows', [])) == 0:
                continue
                
            # 准备分析内容
            requests = []
            for detail in detail_result['datarows']:
                request = {
                    'timestamp': detail[0],
                    'uri': detail[1],
                    'headers': detail[2],
                    'args': detail[3]
                }
                requests.append(request)
                
            # 调用Claude分析
            system_prompt = "你是一个网络安全专家，请分析以下Web访问日志，判断是否存在异常行为。"
            user_prompt = f"分析来自IP {ip}（国家：{country}）在过去24小时内的{count}次访问，重点关注：\n1. 访问模式是否正常\n2. 是否存在自动化工具特征\n3. 是否有潜在的安全风险\n4. 建议采取的措施"
            
            analysis = claude_handler.analyze_content(system_prompt, user_prompt, json.dumps(requests, indent=2))
            
            if analysis:
                message += f'\nIP: {ip}\n国家: {country}\n访问次数: {count}\nJA3: {ja3}\n分析结果:\n{analysis}\n'
                
                # 记录到MySQL
                record = {
                    'ip': ip,
                    'ja3': ja3,
                    'country': country,
                    'count': count,
                    'analysis': analysis,
                    'status': 'ANALYZED'
                }
                mysql_handler.insert_record('ip_analysis', record)
        
        return message if message != '检测到以下IP访问频率异常:\n' else '无异常IP访问模式'
            
    except Exception as e:
        print(f"Error in task_execute: {e}")
        return f'任务执行出错: {str(e)}'