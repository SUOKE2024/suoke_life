"""
privacy_middleware - 索克生活项目模块
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import json
import re

# -*- coding: utf-8 -*-
"""
敏感数据脱敏中间件示例
适用于FastAPI等Python微服务
"""

# 脱敏函数

def mask_phone(phone: str) -> str:
    return re.sub(r'(\d{3})\d{4}(\d{4})', r'\1****\2', phone)

def mask_id_card(id_card: str) -> str:
    return re.sub(r'(\d{4})\d{10}(\w{4})', r'\1**********\2', id_card)

def mask_name(name: str) -> str:
    if len(name) <= 1:
        return '*'
    return name[0] + '*' * (len(name) - 1)

# 脱敏中间件
class PrivacyMaskingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if response.headers.get('content-type', '').startswith('application/json'):
            body = b''
            async for chunk in response.body_iterator:
                body += chunk
            try:
                data = json.loads(body)
                def mask(obj):
                    if isinstance(obj, dict):
                        return {k: mask_phone(v) if 'phone' in k.lower() else \
                                    mask_id_card(v) if 'id' in k.lower() else \
                                    mask_name(v) if 'name' in k.lower() else mask(v)
                                for k, v in obj.items()}
                    elif isinstance(obj, list):
                        return [mask(i) for i in obj]
                    else:
                        return obj
                masked = mask(data)
                return Response(content=json.dumps(masked, ensure_ascii=False),
                                status_code=response.status_code,
                                headers=dict(response.headers),
                                media_type='application/json')
            except Exception:
                return response
        return response

# 用法示例（FastAPI）
# from fastapi import FastAPI
# app = FastAPI()
# app.add_middleware(PrivacyMaskingMiddleware) 