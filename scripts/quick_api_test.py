#!/usr/bin/env python3
"""
快速API测试
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
print(f"API Key: {api_key[:20]}...")

try:
    response = requests.post('https://llm.submodel.ai/v1/chat/completions', 
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        },
        json={
            'model': 'deepseek-ai/DeepSeek-V3.1',
            'messages': [
                {
                    'role': 'user',
                    'content': 'Hello, just say "API works!"'
                }
            ],
            'temperature': 0.7,
            'max_tokens': 20
        },
        timeout=15
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("✅ API调用成功!")
        if 'choices' in data:
            print(f"Response: {data['choices'][0]['message']['content']}")
    else:
        print(f"❌ 错误: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ 异常: {e}")