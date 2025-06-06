"""
generate_api_docs - 索克生活项目模块
"""

    import argparse
from datetime import datetime
from typing import Any
from typing import Optional, Dict, Any
import json
import os
import requests
import sys
import yaml

#!/usr/bin/env python3

"""
API文档生成器
自动生成accessibility-service的API文档
"""



# 添加服务路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'internal', 'service'))


class APIDocGenerator:
    """API文档生成器"""

    def __init__(self, output_dir: str = "docs/api"):
        """
        初始化文档生成器

        Args:
            output_dir: 输出目录
        """
        self.output_dir = output_dir
        self.service_info = {
            'name': 'Accessibility Service',
            'version': '1.0.0',
            'description': '索克生活无障碍服务API',
            'base_url': 'https://api.suoke.life/accessibility/v1'
        }

        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)

    def generate_all_docs(self):
        """生成所有文档"""
        print("🚀 开始生成API文档...")

        # 生成OpenAPI规范
        self.generate_openapi_spec()

        # 生成Markdown文档
        self.generate_markdown_docs()

        # 生成Postman集合
        self.generate_postman_collection()

        # 生成SDK示例
        self.generate_sdk_examples()

        print(f"✅ API文档生成完成，输出目录: {self.output_dir}")

    def generate_openapi_spec(self):
        """生成OpenAPI 3.0规范"""
        spec = {
            "openapi": "3.0.3",
            "info": {
                "title": self.service_info['name'],
                "version": self.service_info['version'],
                "description": self.service_info['description'],
                "contact": {
                    "name": "索克生活技术团队",
                    "email": "tech@suoke.life",
                    "url": "https://suoke.life"
                },
                "license": {
                    "name": "MIT",
                    "url": "https://opensource.org/licenses/MIT"
                }
            },
            "servers": [
                {
                    "url": self.service_info['base_url'],
                    "description": "生产环境"
                },
                {
                    "url": "https://api-staging.suoke.life/accessibility/v1",
                    "description": "测试环境"
                }
            ],
            "paths": self._generate_paths(),
            "components": self._generate_components(),
            "security": [
                {"BearerAuth": []},
                {"ApiKeyAuth": []}
            ]
        }

        # 保存OpenAPI规范
        with open(os.path.join(self.output_dir, 'openapi.yaml'), 'w', encoding='utf-8') as f:
            yaml.dump(spec, f, default_flow_style=False, allow_unicode=True)

        with open(os.path.join(self.output_dir, 'openapi.json'), 'w', encoding='utf-8') as f:
            json.dump(spec, f, indent=2, ensure_ascii=False)

        print("✅ OpenAPI规范生成完成")

    def _generate_paths(self) -> dict[str, Any]:
        """生成API路径"""
        paths = {}

        # 导盲服务API
        paths.update(self._generate_blind_assistance_paths())

        # 语音助手API
        paths.update(self._generate_voice_assistance_paths())

        # 手语识别API
        paths.update(self._generate_sign_language_paths())

        # 屏幕阅读API
        paths.update(self._generate_screen_reading_paths())

        # 内容转换API
        paths.update(self._generate_content_conversion_paths())

        # 健康检查API
        paths.update(self._generate_health_check_paths())

        return paths

    def _generate_blind_assistance_paths(self) -> dict[str, Any]:
        """生成导盲服务API路径"""
        return {
            "/blind-assistance/analyze-scene": {
                "post": {
                    "tags": ["导盲服务"],
                    "summary": "场景分析",
                    "description": "分析图像或视频中的场景，识别障碍物和导航信息",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "multipart/form-data": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "user_id": {"type": "string", "description": "用户ID"},
                                        "image": {"type": "string", "format": "binary", "description": "图像文件"},
                                        "location": {"$ref": "#/components/schemas/Location"}
                                    },
                                    "required": ["user_id", "image"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "场景分析成功",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/SceneAnalysisResponse"}
                                }
                            }
                        },
                        "400": {"$ref": "#/components/responses/BadRequest"},
                        "401": {"$ref": "#/components/responses/Unauthorized"},
                        "500": {"$ref": "#/components/responses/InternalError"}
                    }
                }
            },
            "/blind-assistance/detect-obstacles": {
                "post": {
                    "tags": ["导盲服务"],
                    "summary": "障碍物检测",
                    "description": "检测图像中的障碍物并提供导航建议",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "multipart/form-data": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "user_id": {"type": "string"},
                                        "image": {"type": "string", "format": "binary"},
                                        "detection_sensitivity": {"type": "number", "minimum": 0, "maximum": 1}
                                    },
                                    "required": ["user_id", "image"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "障碍物检测成功",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ObstacleDetectionResponse"}
                                }
                            }
                        }
                    }
                }
            },
            "/blind-assistance/navigation-guidance": {
                "post": {
                    "tags": ["导盲服务"],
                    "summary": "导航指导",
                    "description": "提供基于场景分析的导航指导",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "user_id": {"type": "string"},
                                        "current_location": {"$ref": "#/components/schemas/Location"},
                                        "destination": {"$ref": "#/components/schemas/Location"},
                                        "scene_data": {"type": "object"}
                                    },
                                    "required": ["user_id", "current_location"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "导航指导成功",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/NavigationResponse"}
                                }
                            }
                        }
                    }
                }
            }
        }

    def _generate_voice_assistance_paths(self) -> dict[str, Any]:
        """生成语音助手API路径"""
        return {
            "/voice-assistance/speech-to-text": {
                "post": {
                    "tags": ["语音助手"],
                    "summary": "语音转文字",
                    "description": "将语音音频转换为文字",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "multipart/form-data": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "user_id": {"type": "string"},
                                        "audio": {"type": "string", "format": "binary"},
                                        "language": {"type": "string", "default": "zh-CN"},
                                        "format": {"type": "string", "enum": ["wav", "mp3", "m4a"]}
                                    },
                                    "required": ["user_id", "audio"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "语音转文字成功",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/SpeechToTextResponse"}
                                }
                            }
                        }
                    }
                }
            },
            "/voice-assistance/text-to-speech": {
                "post": {
                    "tags": ["语音助手"],
                    "summary": "文字转语音",
                    "description": "将文字转换为语音音频",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "user_id": {"type": "string"},
                                        "text": {"type": "string"},
                                        "voice": {"type": "string", "default": "female"},
                                        "speed": {"type": "number", "minimum": 0.5, "maximum": 2.0, "default": 1.0},
                                        "format": {"type": "string", "enum": ["wav", "mp3"], "default": "mp3"}
                                    },
                                    "required": ["user_id", "text"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "文字转语音成功",
                            "content": {
                                "audio/mpeg": {
                                    "schema": {"type": "string", "format": "binary"}
                                }
                            }
                        }
                    }
                }
            }
        }

    def _generate_sign_language_paths(self) -> dict[str, Any]:
        """生成手语识别API路径"""
        return {
            "/sign-language/recognize": {
                "post": {
                    "tags": ["手语识别"],
                    "summary": "手语识别",
                    "description": "识别视频中的手语动作并转换为文字",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "multipart/form-data": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "user_id": {"type": "string"},
                                        "video": {"type": "string", "format": "binary"},
                                        "language": {"type": "string", "default": "csl"}
                                    },
                                    "required": ["user_id", "video"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "手语识别成功",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/SignLanguageResponse"}
                                }
                            }
                        }
                    }
                }
            }
        }

    def _generate_screen_reading_paths(self) -> dict[str, Any]:
        """生成屏幕阅读API路径"""
        return {
            "/screen-reading/read-content": {
                "post": {
                    "tags": ["屏幕阅读"],
                    "summary": "内容阅读",
                    "description": "读取并解析屏幕内容",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "user_id": {"type": "string"},
                                        "content": {"type": "string"},
                                        "content_type": {"type": "string", "enum": ["html", "text", "pdf"]},
                                        "reading_speed": {"type": "string", "enum": ["slow", "normal", "fast"]}
                                    },
                                    "required": ["user_id", "content"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "内容阅读成功",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ScreenReadingResponse"}
                                }
                            }
                        }
                    }
                }
            }
        }

    def _generate_content_conversion_paths(self) -> dict[str, Any]:
        """生成内容转换API路径"""
        return {
            "/content-conversion/convert": {
                "post": {
                    "tags": ["内容转换"],
                    "summary": "内容格式转换",
                    "description": "转换内容格式以提高可访问性",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "multipart/form-data": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "user_id": {"type": "string"},
                                        "file": {"type": "string", "format": "binary"},
                                        "source_format": {"type": "string"},
                                        "target_format": {"type": "string"},
                                        "accessibility_options": {"type": "object"}
                                    },
                                    "required": ["user_id", "file", "target_format"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "内容转换成功",
                            "content": {
                                "application/octet-stream": {
                                    "schema": {"type": "string", "format": "binary"}
                                }
                            }
                        }
                    }
                }
            }
        }

    def _generate_health_check_paths(self) -> dict[str, Any]:
        """生成健康检查API路径"""
        return {
            "/health": {
                "get": {
                    "tags": ["系统"],
                    "summary": "健康检查",
                    "description": "检查服务健康状态",
                    "responses": {
                        "200": {
                            "description": "服务健康",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/HealthResponse"}
                                }
                            }
                        }
                    }
                }
            },
            "/health/ready": {
                "get": {
                    "tags": ["系统"],
                    "summary": "就绪检查",
                    "description": "检查服务是否就绪",
                    "responses": {
                        "200": {"description": "服务就绪"},
                        "503": {"description": "服务未就绪"}
                    }
                }
            },
            "/health/live": {
                "get": {
                    "tags": ["系统"],
                    "summary": "存活检查",
                    "description": "检查服务是否存活",
                    "responses": {
                        "200": {"description": "服务存活"}
                    }
                }
            }
        }

    def _generate_components(self) -> dict[str, Any]:
        """生成组件定义"""
        return {
            "schemas": {
                "Location": {
                    "type": "object",
                    "properties": {
                        "latitude": {"type": "number"},
                        "longitude": {"type": "number"},
                        "altitude": {"type": "number"}
                    },
                    "required": ["latitude", "longitude"]
                },
                "SceneAnalysisResponse": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string"},
                        "timestamp": {"type": "string", "format": "date-time"},
                        "scene_description": {"type": "string"},
                        "objects": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "type": {"type": "string"},
                                    "confidence": {"type": "number"},
                                    "position": {"type": "object"}
                                }
                            }
                        },
                        "navigation_suggestions": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "ObstacleDetectionResponse": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string"},
                        "timestamp": {"type": "string", "format": "date-time"},
                        "obstacles": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "type": {"type": "string"},
                                    "distance": {"type": "number"},
                                    "direction": {"type": "string"},
                                    "severity": {"type": "string", "enum": ["low", "medium", "high"]}
                                }
                            }
                        },
                        "safe_path": {"type": "object"}
                    }
                },
                "NavigationResponse": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string"},
                        "timestamp": {"type": "string", "format": "date-time"},
                        "instructions": {"type": "array", "items": {"type": "string"}},
                        "estimated_time": {"type": "number"},
                        "difficulty_level": {"type": "string"}
                    }
                },
                "SpeechToTextResponse": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string"},
                        "timestamp": {"type": "string", "format": "date-time"},
                        "text": {"type": "string"},
                        "confidence": {"type": "number"},
                        "language": {"type": "string"}
                    }
                },
                "SignLanguageResponse": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string"},
                        "timestamp": {"type": "string", "format": "date-time"},
                        "recognized_text": {"type": "string"},
                        "confidence": {"type": "number"},
                        "gestures": {"type": "array", "items": {"type": "object"}}
                    }
                },
                "ScreenReadingResponse": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string"},
                        "timestamp": {"type": "string", "format": "date-time"},
                        "processed_content": {"type": "string"},
                        "reading_time": {"type": "number"},
                        "accessibility_score": {"type": "number"}
                    }
                },
                "HealthResponse": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["healthy", "degraded", "unhealthy"]},
                        "timestamp": {"type": "string", "format": "date-time"},
                        "version": {"type": "string"},
                        "uptime_seconds": {"type": "integer"},
                        "checks": {"type": "object"}
                    }
                },
                "Error": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string"},
                        "message": {"type": "string"},
                        "details": {"type": "object"}
                    }
                }
            },
            "responses": {
                "BadRequest": {
                    "description": "请求参数错误",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/Error"}
                        }
                    }
                },
                "Unauthorized": {
                    "description": "未授权访问",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/Error"}
                        }
                    }
                },
                "InternalError": {
                    "description": "服务器内部错误",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/Error"}
                        }
                    }
                }
            },
            "securitySchemes": {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
                },
                "ApiKeyAuth": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-API-Key"
                }
            }
        }

    def generate_markdown_docs(self):
        """生成Markdown文档"""
        # 生成主文档
        main_doc = self._generate_main_markdown()
        with open(os.path.join(self.output_dir, 'README.md'), 'w', encoding='utf-8') as f:
            f.write(main_doc)

        # 生成各服务的详细文档
        services = [
            ('blind_assistance', '导盲服务'),
            ('voice_assistance', '语音助手'),
            ('sign_language', '手语识别'),
            ('screen_reading', '屏幕阅读'),
            ('content_conversion', '内容转换')
        ]

        for service_id, service_name in services:
            doc = self._generate_service_markdown(service_id, service_name)
            with open(os.path.join(self.output_dir, f'{service_id}.md'), 'w', encoding='utf-8') as f:
                f.write(doc)

        print("✅ Markdown文档生成完成")

    def _generate_main_markdown(self) -> str:
        """生成主Markdown文档"""
        return f"""# {self.service_info['name']} API文档

## 概述

{self.service_info['description']}

**版本**: {self.service_info['version']}
**基础URL**: `{self.service_info['base_url']}`

## 快速开始

### 认证

本API支持两种认证方式：

1. **Bearer Token (JWT)**
   ```
   Authorization: Bearer <your-jwt-token>
   ```

2. **API Key**
   ```
   X-API-Key: <your-api-key>
   ```

### 基本请求示例

```bash
curl -X POST "{self.service_info['base_url']}/blind-assistance/analyze-scene" \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -H "Content-Type: multipart/form-data" \\
  -F "user_id=user123" \\
  -F "image=@scene.jpg"
```

## 服务模块

### 🦮 [导盲服务](./blind_assistance.md)
- 场景分析
- 障碍物检测
- 导航指导

### 🎤 [语音助手](./voice_assistance.md)
- 语音转文字
- 文字转语音
- 语音命令处理

### 🤟 [手语识别](./sign_language.md)
- 手语动作识别
- 手语翻译
- 实时手语交流

### 📖 [屏幕阅读](./screen_reading.md)
- 内容解析
- 语音播报
- 可访问性优化

### 🔄 [内容转换](./content_conversion.md)
- 格式转换
- 可访问性增强
- 多媒体处理

## 错误处理

API使用标准HTTP状态码：

- `200` - 成功
- `400` - 请求参数错误
- `401` - 未授权
- `403` - 禁止访问
- `404` - 资源不存在
- `429` - 请求频率限制
- `500` - 服务器内部错误

错误响应格式：
```json
{{
  "code": "INVALID_PARAMETER",
  "message": "参数user_id不能为空",
  "details": {{
    "field": "user_id",
    "value": null
  }}
}}
```

## 速率限制

- 全局限制：1000次/分钟
- 用户限制：100次/分钟
- IP限制：200次/分钟

## SDK和工具

- [Python SDK](./sdk/python.md)
- [JavaScript SDK](./sdk/javascript.md)
- [Postman集合](./postman_collection.json)

## 支持

- 📧 邮箱：tech@suoke.life
- 📖 文档：https://docs.suoke.life
- 🐛 问题反馈：https://github.com/suoke-life/issues

---

*最后更新：{datetime.now().strftime('%Y-%m-%d')}*
"""

    def _generate_service_markdown(self, service_id: str, service_name: str) -> str:
        """生成服务Markdown文档"""
        return f"""# {service_name} API

## 概述

{service_name}提供专业的无障碍辅助功能。

## 端点

### POST /{service_id}/...

详细的API端点文档...

## 示例

### 请求示例

```bash
curl -X POST "{self.service_info['base_url']}/{service_id}/..." \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{{"user_id": "user123"}}'
```

### 响应示例

```json
{{
  "user_id": "user123",
  "timestamp": "2024-01-01T00:00:00Z",
  "result": "..."
}}
```

## 错误码

| 错误码 | 描述 | 解决方案 |
|--------|------|----------|
| E001 | 参数错误 | 检查请求参数 |
| E002 | 文件格式不支持 | 使用支持的文件格式 |

---

[返回主文档](./README.md)
"""

    def generate_postman_collection(self):
        """生成Postman集合"""
        collection = {
            "info": {
                "name": f"{self.service_info['name']} API",
                "description": self.service_info['description'],
                "version": self.service_info['version'],
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "auth": {
                "type": "bearer",
                "bearer": [
                    {
                        "key": "token",
                        "value": "{{access_token}}",
                        "type": "string"
                    }
                ]
            },
            "variable": [
                {
                    "key": "base_url",
                    "value": self.service_info['base_url'],
                    "type": "string"
                },
                {
                    "key": "access_token",
                    "value": "your-jwt-token-here",
                    "type": "string"
                }
            ],
            "item": self._generate_postman_items()
        }

        with open(os.path.join(self.output_dir, 'postman_collection.json'), 'w', encoding='utf-8') as f:
            json.dump(collection, f, indent=2, ensure_ascii=False)

        print("✅ Postman集合生成完成")

    def _generate_postman_items(self) -> list[dict[str, Any]]:
        """生成Postman请求项"""
        return [
            {
                "name": "导盲服务",
                "item": [
                    {
                        "name": "场景分析",
                        "request": {
                            "method": "POST",
                            "header": [],
                            "body": {
                                "mode": "formdata",
                                "formdata": [
                                    {"key": "user_id", "value": "user123", "type": "text"},
                                    {"key": "image", "type": "file"}
                                ]
                            },
                            "url": {
                                "raw": "{{base_url}}/blind-assistance/analyze-scene",
                                "host": ["{{base_url}}"],
                                "path": ["blind-assistance", "analyze-scene"]
                            }
                        }
                    }
                ]
            },
            {
                "name": "语音助手",
                "item": [
                    {
                        "name": "语音转文字",
                        "request": {
                            "method": "POST",
                            "header": [],
                            "body": {
                                "mode": "formdata",
                                "formdata": [
                                    {"key": "user_id", "value": "user123", "type": "text"},
                                    {"key": "audio", "type": "file"}
                                ]
                            },
                            "url": {
                                "raw": "{{base_url}}/voice-assistance/speech-to-text",
                                "host": ["{{base_url}}"],
                                "path": ["voice-assistance", "speech-to-text"]
                            }
                        }
                    }
                ]
            },
            {
                "name": "系统",
                "item": [
                    {
                        "name": "健康检查",
                        "request": {
                            "method": "GET",
                            "header": [],
                            "url": {
                                "raw": "{{base_url}}/health",
                                "host": ["{{base_url}}"],
                                "path": ["health"]
                            }
                        }
                    }
                ]
            }
        ]

    def generate_sdk_examples(self):
        """生成SDK示例"""
        # 创建SDK目录
        sdk_dir = os.path.join(self.output_dir, 'sdk')
        os.makedirs(sdk_dir, exist_ok=True)

        # Python SDK示例
        python_example = self._generate_python_sdk_example()
        with open(os.path.join(sdk_dir, 'python_example.py'), 'w', encoding='utf-8') as f:
            f.write(python_example)

        # JavaScript SDK示例
        js_example = self._generate_javascript_sdk_example()
        with open(os.path.join(sdk_dir, 'javascript_example.js'), 'w', encoding='utf-8') as f:
            f.write(js_example)

        print("✅ SDK示例生成完成")

    def _generate_python_sdk_example(self) -> str:
        """生成Python SDK示例"""
        return '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
索克生活无障碍服务 Python SDK 示例
"""



class AccessibilityServiceClient:
    """无障碍服务客户端"""

    def __init__(self, base_url: str, token: str):
        """
        初始化客户端

        Args:
            base_url: API基础URL
            token: 认证令牌
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {token}',
            'User-Agent': 'SuokeLife-AccessibilityService-Python-SDK/1.0.0'
        })

    def analyze_scene(self, user_id: str, image_path: str,
                     location: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        场景分析

        Args:
            user_id: 用户ID
            image_path: 图像文件路径
            location: 位置信息

        Returns:
            场景分析结果
        """
        url = f"{self.base_url}/blind-assistance/analyze-scene"

        data = {'user_id': user_id}
        if location:
            data['location'] = json.dumps(location)

        with open(image_path, 'rb') as f:
            files = {'image': f}
            response = self.session.post(url, data=data, files=files)

        response.raise_for_status()
        return response.json()

    def speech_to_text(self, user_id: str, audio_path: str,
                      language: str = 'zh-CN') -> Dict[str, Any]:
        """
        语音转文字

        Args:
            user_id: 用户ID
            audio_path: 音频文件路径
            language: 语言代码

        Returns:
            转换结果
        """
        url = f"{self.base_url}/voice-assistance/speech-to-text"

        data = {
            'user_id': user_id,
            'language': language
        }

        with open(audio_path, 'rb') as f:
            files = {'audio': f}
            response = self.session.post(url, data=data, files=files)

        response.raise_for_status()
        return response.json()

    def text_to_speech(self, user_id: str, text: str,
                      voice: str = 'female', speed: float = 1.0) -> bytes:
        """
        文字转语音

        Args:
            user_id: 用户ID
            text: 要转换的文字
            voice: 语音类型
            speed: 语速

        Returns:
            音频数据
        """
        url = f"{self.base_url}/voice-assistance/text-to-speech"

        data = {
            'user_id': user_id,
            'text': text,
            'voice': voice,
            'speed': speed
        }

        response = self.session.post(url, json=data)
        response.raise_for_status()
        return response.content

    def check_health(self) -> Dict[str, Any]:
        """
        检查服务健康状态

        Returns:
            健康状态信息
        """
        url = f"{self.base_url}/health"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()


# 使用示例
if __name__ == '__main__':
    # 初始化客户端
    client = AccessibilityServiceClient(
        base_url='https://api.suoke.life/accessibility/v1',
        token='your-jwt-token-here'
    )

    try:
        # 检查服务健康状态
        health = client.check_health()
        print(f"服务状态: {health['status']}")

        # 场景分析示例
        result = client.analyze_scene(
            user_id='user123',
            image_path='scene.jpg',
            location={'latitude': 39.9042, 'longitude': 116.4074}
        )
        print(f"场景分析结果: {result['scene_description']}")

        # 语音转文字示例
        stt_result = client.speech_to_text(
            user_id='user123',
            audio_path='speech.wav'
        )
        print(f"识别文字: {stt_result['text']}")

        # 文字转语音示例
        audio_data = client.text_to_speech(
            user_id='user123',
            text='欢迎使用索克生活无障碍服务'
        )

        with open('output.mp3', 'wb') as f:
            f.write(audio_data)
        print("语音文件已保存为 output.mp3")

    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
    except Exception as e:
        print(f"错误: {e}")
'''

    def _generate_javascript_sdk_example(self) -> str:
        """生成JavaScript SDK示例"""
        return r'''/**
 * 索克生活无障碍服务 JavaScript SDK 示例
 */

class AccessibilityServiceClient {
    /**
     * 初始化客户端
     * @param {string} baseUrl - API基础URL
     * @param {string} token - 认证令牌
     */
    constructor(baseUrl, token) {
        this.baseUrl = baseUrl.replace(/\/$/, '');
        this.token = token;
        this.headers = {
            'Authorization': `Bearer ${token}`,
            'User-Agent': 'SuokeLife-AccessibilityService-JS-SDK/1.0.0'
        };
    }

    /**
     * 场景分析
     * @param {string} userId - 用户ID
     * @param {File} imageFile - 图像文件
     * @param {Object} location - 位置信息
     * @returns {Promise<Object>} 场景分析结果
     */
    async analyzeScene(userId, imageFile, location = null) {
        const url = `${this.baseUrl}/blind-assistance/analyze-scene`;

        const formData = new FormData();
        formData.append('user_id', userId);
        formData.append('image', imageFile);

        if (location) {
            formData.append('location', JSON.stringify(location));
        }

        const response = await fetch(url, {
            method: 'POST',
            headers: this.headers,
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }

    /**
     * 语音转文字
     * @param {string} userId - 用户ID
     * @param {File} audioFile - 音频文件
     * @param {string} language - 语言代码
     * @returns {Promise<Object>} 转换结果
     */
    async speechToText(userId, audioFile, language = 'zh-CN') {
        const url = `${this.baseUrl}/voice-assistance/speech-to-text`;

        const formData = new FormData();
        formData.append('user_id', userId);
        formData.append('audio', audioFile);
        formData.append('language', language);

        const response = await fetch(url, {
            method: 'POST',
            headers: this.headers,
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }

    /**
     * 文字转语音
     * @param {string} userId - 用户ID
     * @param {string} text - 要转换的文字
     * @param {string} voice - 语音类型
     * @param {number} speed - 语速
     * @returns {Promise<Blob>} 音频数据
     */
    async textToSpeech(userId, text, voice = 'female', speed = 1.0) {
        const url = `${this.baseUrl}/voice-assistance/text-to-speech`;

        const response = await fetch(url, {
            method: 'POST',
            headers: {
                ...this.headers,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: userId,
                text: text,
                voice: voice,
                speed: speed
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.blob();
    }

    /**
     * 检查服务健康状态
     * @returns {Promise<Object>} 健康状态信息
     */
    async checkHealth() {
        const url = `${this.baseUrl}/health`;

        const response = await fetch(url, {
            method: 'GET',
            headers: this.headers
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }
}

// 使用示例
async function example() {
    // 初始化客户端
    const client = new AccessibilityServiceClient(
        'https://api.suoke.life/accessibility/v1',
        'your-jwt-token-here'
    );

    try {
        // 检查服务健康状态
        const health = await client.checkHealth();
        console.log(`服务状态: ${health.status}`);

        // 场景分析示例（需要文件输入）
        const imageInput = document.getElementById('imageInput');
        if (imageInput.files.length > 0) {
            const result = await client.analyzeScene(
                'user123',
                imageInput.files[0],
                { latitude: 39.9042, longitude: 116.4074 }
            );
            console.log(`场景分析结果: ${result.scene_description}`);
        }

        // 语音转文字示例（需要音频输入）
        const audioInput = document.getElementById('audioInput');
        if (audioInput.files.length > 0) {
            const sttResult = await client.speechToText(
                'user123',
                audioInput.files[0]
            );
            console.log(`识别文字: ${sttResult.text}`);
        }

        // 文字转语音示例
        const audioBlob = await client.textToSpeech(
            'user123',
            '欢迎使用索克生活无障碍服务'
        );

        // 播放音频
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        audio.play();

    } catch (error) {
        console.error('错误:', error);
    }
}

// 导出客户端类
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AccessibilityServiceClient;
}
'''


def main():
    """主函数"""

    parser = argparse.ArgumentParser(description='生成API文档')
    parser.add_argument('--output', '-o', default='docs/api', help='输出目录')
    args = parser.parse_args()

    generator = APIDocGenerator(args.output)
    generator.generate_all_docs()


if __name__ == '__main__':
    main()
