import boto3
import json

# 调用bedrock claude
# def generate_message_invoke(messages):
#     body=json.dumps(
#         {
#             "anthropic_version": "bedrock-2023-05-31",
#             "max_tokens": max_tokens,
#             "temperature": temperature, 
#             # "top_p": top_p,
#             # "top_k": top_k,
#             "system": system_prompt,
#             "messages": messages
#         }  
#     )  
#     response = bedrock_client.invoke_model(body=body, modelId=model_id,)
#     response_body = json.loads(response.get('body').read())
   
#     return response_body


# bedrock_client = boto3.client(service_name='bedrock-runtime',region_name = 'us-west-2')
# temperature: float = 0.1
# top_k: float = 20
# top_p: float = 0.1
# max_tokens: int = 4096
# # model_id: str = 'anthropic.claude-3-5-sonnet-20241022-v2:0'    
# # model_id: str ='us.anthropic.claude-3-5-sonnet-20241022-v2:0'
# model_id: str ='us.amazon.nova-pro-v1:0'
# system_prompt: str = ''



#claude请求
def run_multi_modal_prompt(system, messages, model_id):
    inf_params = {"maxTokens": max_tokens, "topP": top_p, "temperature": temperature}
    additionalModelRequestFields = {
    "inferenceConfig": {
         "topK": top_k
        }
    }
    
    response = bedrock_client.converse(
        modelId=model_id, 
        messages=messages, 
        system=system, 
        inferenceConfig=inf_params
    )

    return response

def generate_message(system_prompt,user_prompt,assistant_content):
    # model_id = 'us.amazon.nova-pro-v1:0'
    model_id = 'us.anthropic.claude-3-5-sonnet-20241022-v2:0'
    
    messages = [{
        "role": "user",
        "content": [
            {
                "text": user_prompt
            }
            ]
        },
        {
        "role": "assistant",
        "content":[
            {
                "text": assistant_content
            }
            ]
        }]
        
    system = [{ "text": system_prompt}]
    response = run_multi_modal_prompt(system, messages, model_id)
    print('getInfoInsight')
    print(response["usage"]["inputTokens"],response["usage"]["outputTokens"])
    return f'检测{response["output"]["message"]["content"][0]["text"]}'


bedrock_client = boto3.client(service_name='bedrock-runtime',region_name='us-west-2')
temperature = 0.1
top_k = 20
top_p = 0.1
max_tokens = 4096