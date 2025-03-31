import boto3
import json

def analyze_content(system_prompt, user_prompt, content):
    try:
        bedrock = boto3.client('bedrock-runtime')
        
        # 构建请求体
        body = {
            "prompt": f"\n\nHuman: {system_prompt}\n\n{user_prompt}\n\ncontent:{content}\n\nAssistant:",
            "max_tokens": 2048,
            "temperature": 0,
            "top_p": 0.9
        }
        
        # 调用Bedrock API
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-sonnet-20240229-v1:0',
            body=json.dumps(body)
        )
        
        # 解析响应
        response_body = json.loads(response['body'].read())
        return response_body['completion']
        
    except Exception as e:
        print(f"Error in analyze_content: {e}")
        return None