#!/usr/bin/env python3
import os
import sys
import json
from pathlib import Path

def load_env():
    """Load environment variables from .env file"""
    env_path = Path('.env')
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    else:
        print("Warning: .env file not found")

def test_connection():
    try:
        import volcengine
        from volcengine.ark import ArkClient
        
        # 获取 API key
        api_key = os.getenv('ARK_API_KEY')
        if not api_key:
            print("Error: ARK_API_KEY not found in environment variables")
            return False
        
        # 初始化客户端
        client = ArkClient(api_key)
        
        # 发送测试请求
        messages = [{"role": "user", "content": "你好"}]
        print("Sending request:", json.dumps(messages, ensure_ascii=False))
        
        response = client.chat.completions.create(
            model="ep-20241212093835-bl92q",
            messages=messages
        )
        
        print("Response:", response.output.choices[0].message.content)
        return True
        
    except ImportError as e:
        print("Error: Please install required package:")
        print("pip3 install 'volcengine-python-sdk[ark]'")
        return False
    except Exception as e:
        print("Error:", str(e))
        return False

if __name__ == '__main__':
    load_env()
    test_connection() 