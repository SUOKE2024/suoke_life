"""
generate_api_docs - 索克生活项目模块
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
import ast
import json
import logging
import os
import re
import requests

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
索克生活 - API文档自动生成器
自动扫描所有微服务，生成完整的API文档
"""


# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class APIDocumentationGenerator:
    """API文档生成器"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.services_dir = self.project_root / "services"
        self.docs_dir = self.project_root / "docs" / "api"
        self.docs_dir.mkdir(parents=True, exist_ok=True)

        # 微服务列表
        self.services = [
            "agent-services/xiaoai-service",
            "agent-services/xiaoke-service", 
            "agent-services/laoke-service",
            "agent-services/soer-service",
            "health-data-service",
            "blockchain-service",
            "auth-service",
            "api-gateway",
            "rag-service",
            "medical-resource-service",
            "message-bus",
            "user-service",
            "diagnostic-services/look-service",
            "diagnostic-services/listen-service",
            "diagnostic-services/inquiry-service",
            "diagnostic-services/palpation-service",
            "diagnostic-services/calculation-service"
        ]

    def generate_all_docs(self) -> bool:
        """生成所有API文档"""
        logger.info("🚀 开始生成API文档...")

        success_count = 0
        total_services = len(self.services)

        for service in self.services:
            try:
                logger.info(f"📝 生成 {service} API文档...")
                if self.generate_service_doc(service):
                    success_count += 1
                    logger.info(f"✅ {service} API文档生成成功")
                else:
                    logger.warning(f"⚠️ {service} API文档生成失败")
            except Exception as e:
                logger.error(f"❌ {service} API文档生成异常: {e}")

        # 生成总览文档
        self.generate_overview_doc()

        logger.info(f"📊 API文档生成完成: {success_count}/{total_services} 成功")
        return success_count == total_services

    def generate_service_doc(self, service: str) -> bool:
        """生成单个服务的API文档"""
        service_path = self.services_dir / service

        if not service_path.exists():
            logger.warning(f"服务目录不存在: {service_path}")
            return False

        # 查找API文件
        api_files = self.find_api_files(service_path)

        if not api_files:
            logger.warning(f"未找到API文件: {service}")
            return False

        # 解析API
        api_info = self.parse_api_files(api_files)

        # 生成文档
        doc_content = self.generate_markdown_doc(service, api_info)

        # 保存文档
        doc_file = self.docs_dir / f"{service.replace('/', '_')}.md"
        doc_file.parent.mkdir(parents=True, exist_ok=True)

        with open(doc_file, 'w', encoding='utf-8') as f:
            f.write(doc_content)

        return True

    def find_api_files(self, service_path: Path) -> List[Path]:
        """查找API文件"""
        api_files = []

        # 常见的API文件模式
        patterns = [
            "**/main.py",
            "**/api*.py", 
            "**/router*.py",
            "**/rest_api.py",
            "**/delivery/**/*.py",
            "**/cmd/server/*.py"
        ]

        for pattern in patterns:
            files = list(service_path.glob(pattern))
            api_files.extend(files)

        # 去重并过滤
        unique_files = []
        seen = set()

        for file in api_files:
            if file.name not in seen and self.is_api_file(file):
                unique_files.append(file)
                seen.add(file.name)

        return unique_files

    def is_api_file(self, file_path: Path) -> bool:
        """判断是否为API文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 检查是否包含FastAPI相关内容
            api_indicators = [
                'from fastapi import',
                '@app.',
                'FastAPI(',
                'APIRouter(',
                '@router.',
                'app = FastAPI'
            ]

            return any(indicator in content for indicator in api_indicators)

        except Exception:
            return False

    def parse_api_files(self, api_files: List[Path]) -> Dict[str, Any]:
        """解析API文件"""
        api_info = {
            "endpoints": [],
            "models": [],
            "description": "",
            "version": "1.0.0"
        }

        for file_path in api_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 解析端点
                endpoints = self.extract_endpoints(content)
                api_info["endpoints"].extend(endpoints)

                # 解析模型
                models = self.extract_models(content)
                api_info["models"].extend(models)

                # 提取描述
                if not api_info["description"]:
                    description = self.extract_description(content)
                    if description:
                        api_info["description"] = description

            except Exception as e:
                logger.warning(f"解析文件失败 {file_path}: {e}")

        return api_info

    def extract_endpoints(self, content: str) -> List[Dict[str, Any]]:
        """提取API端点"""
        endpoints = []

        # 匹配FastAPI路由装饰器
        route_pattern = r'@(?:app|router)\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']'

        matches = re.finditer(route_pattern, content, re.IGNORECASE)

        for match in matches:
            method = match.group(1).upper()
            path = match.group(2)

            # 查找函数定义
            func_start = content.find('def ', match.end())
            if func_start != -1:
                func_end = content.find('\n', func_start)
                func_line = content[func_start:func_end]

                # 提取函数名
                func_name_match = re.search(r'def\s+(\w+)', func_line)
                func_name = func_name_match.group(1) if func_name_match else "unknown"

                # 查找文档字符串
                docstring = self.extract_function_docstring(content, func_start)

                endpoint = {
                    "method": method,
                    "path": path,
                    "function": func_name,
                    "description": docstring or f"{method} {path}",
                    "parameters": [],
                    "responses": {}
                }

                endpoints.append(endpoint)

        return endpoints

    def extract_models(self, content: str) -> List[Dict[str, Any]]:
        """提取数据模型"""
        models = []

        # 匹配Pydantic模型
        model_pattern = r'class\s+(\w+)\s*\([^)]*BaseModel[^)]*\):'

        matches = re.finditer(model_pattern, content)

        for match in matches:
            model_name = match.group(1)

            # 查找类的文档字符串
            class_start = match.start()
            docstring = self.extract_class_docstring(content, class_start)

            model = {
                "name": model_name,
                "description": docstring or f"数据模型: {model_name}",
                "fields": []
            }

            models.append(model)

        return models

    def extract_description(self, content: str) -> Optional[str]:
        """提取模块描述"""
        # 查找模块级文档字符串
        lines = content.split('\n')

        for i, line in enumerate(lines):
            if '"""' in line or "'''" in line:
                # 找到文档字符串开始
                quote = '"""' if '"""' in line else "'''"

                if line.count(quote) >= 2:
                    # 单行文档字符串
                    start = line.find(quote) + 3
                    end = line.rfind(quote)
                    return line[start:end].strip()
                else:
                    # 多行文档字符串
                    desc_lines = []
                    for j in range(i + 1, len(lines)):
                        if quote in lines[j]:
                            break
                        desc_lines.append(lines[j].strip())

                    if desc_lines:
                        return '\n'.join(desc_lines).strip()

        return None

    def extract_function_docstring(self, content: str, func_start: int) -> Optional[str]:
        """提取函数文档字符串"""
        # 简化实现，查找函数后的第一个文档字符串
        func_content = content[func_start:func_start + 1000]  # 限制搜索范围

        lines = func_content.split('\n')
        for i, line in enumerate(lines[1:], 1):  # 跳过函数定义行
            stripped = line.strip()
            if stripped.startswith('"""') or stripped.startswith("'''"):
                quote = '"""' if stripped.startswith('"""') else "'''"

                if stripped.count(quote) >= 2:
                    # 单行文档字符串
                    start = stripped.find(quote) + 3
                    end = stripped.rfind(quote)
                    return stripped[start:end].strip()
                else:
                    # 多行文档字符串
                    desc_lines = []
                    for j in range(i + 1, len(lines)):
                        if quote in lines[j]:
                            break
                        desc_lines.append(lines[j].strip())

                    if desc_lines:
                        return '\n'.join(desc_lines).strip()
            elif stripped and not stripped.startswith('#'):
                # 遇到非注释代码，停止搜索
                break

        return None

    def extract_class_docstring(self, content: str, class_start: int) -> Optional[str]:
        """提取类文档字符串"""
        return self.extract_function_docstring(content, class_start)

    def generate_markdown_doc(self, service: str, api_info: Dict[str, Any]) -> str:
        """生成Markdown文档"""
        service_name = service.replace('/', ' ').replace('-', ' ').title()

        doc = f"""# {service_name} API 文档

## 服务概述

**服务名称**: {service}  
**版本**: {api_info.get('version', '1.0.0')}  
**描述**: {api_info.get('description', f'{service_name} 微服务API接口文档')}

## API 端点

"""

        # 按HTTP方法分组
        methods_groups = {}
        for endpoint in api_info["endpoints"]:
            method = endpoint["method"]
            if method not in methods_groups:
                methods_groups[method] = []
            methods_groups[method].append(endpoint)

        for method in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
            if method in methods_groups:
                doc += f"### {method} 请求\n\n"

                for endpoint in methods_groups[method]:
                    doc += f"#### {method} {endpoint['path']}\n\n"
                    doc += f"**功能**: {endpoint['description']}\n\n"
                    doc += f"**函数**: `{endpoint['function']}`\n\n"

                    # 请求参数
                    if endpoint.get('parameters'):
                        doc += "**请求参数**:\n\n"
                        for param in endpoint['parameters']:
                            doc += f"- `{param['name']}` ({param['type']}): {param['description']}\n"
                        doc += "\n"

                    # 响应示例
                    doc += "**响应示例**:\n\n"
                    doc += "```json\n"
                    doc += "{\n"
                    doc += '  "code": 200,\n'
                    doc += '  "message": "success",\n'
                    doc += '  "data": {}\n'
                    doc += "}\n"
                    doc += "```\n\n"

                    doc += "---\n\n"

        # 数据模型
        if api_info["models"]:
            doc += "## 数据模型\n\n"

            for model in api_info["models"]:
                doc += f"### {model['name']}\n\n"
                doc += f"{model['description']}\n\n"

                if model.get('fields'):
                    doc += "**字段说明**:\n\n"
                    for field in model['fields']:
                        doc += f"- `{field['name']}` ({field['type']}): {field['description']}\n"
                    doc += "\n"

                doc += "```python\n"
                doc += f"class {model['name']}(BaseModel):\n"
                doc += "    # 字段定义\n"
                doc += "    pass\n"
                doc += "```\n\n"

        # 错误码
        doc += """## 错误码说明

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 200 | 请求成功 | - |
| 400 | 请求参数错误 | 检查请求参数格式 |
| 401 | 未授权访问 | 检查认证信息 |
| 403 | 权限不足 | 联系管理员 |
| 404 | 资源不存在 | 检查请求路径 |
| 500 | 服务器内部错误 | 联系技术支持 |

## 使用示例

### Python 示例

```python

# 基础URL
BASE_URL = "http://localhost:8000"

# 示例请求
response = requests.get(f"{BASE_URL}/api/v1/health")
print(response.json())
```

### cURL 示例

```bash
# 健康检查
curl -X GET "http://localhost:8000/api/v1/health"

# 带认证的请求
curl -X GET "http://localhost:8000/api/v1/data" \\
-H "Authorization: Bearer YOUR_TOKEN"
```

## 联系信息

- **技术支持**: tech@suoke.life
- **文档更新**: 2025年6月6日
- **维护团队**: 索克生活技术团队

"""

        return doc

    def generate_overview_doc(self) -> None:
        """生成API总览文档"""
        overview_content = """# 索克生活 API 文档总览

## 微服务架构概述

索克生活采用微服务架构，包含以下核心服务：

## 智能体服务群

### 1. 小艾智能体服务 (xiaoai-service)
- **功能**: 健康助手 & 首页聊天频道版主
- **端口**: 8001
- **文档**: [xiaoai-service API](./agent-services_xiaoai-service.md)

### 2. 小克智能体服务 (xiaoke-service)  
- **功能**: 健康数据分析师 & 个人健康档案管理员
- **端口**: 8002
- **文档**: [xiaoke-service API](./agent-services_xiaoke-service.md)

### 3. 老克智能体服务 (laoke-service)
- **功能**: 中医专家 & 辨证论治决策支持
- **端口**: 8003
- **文档**: [laoke-service API](./agent-services_laoke-service.md)

### 4. 索儿智能体服务 (soer-service)
- **功能**: 生活方式顾问 & 健康行为引导师
- **端口**: 8004
- **文档**: [soer-service API](./agent-services_soer-service.md)

## 核心业务服务

### 5. 健康数据服务 (health-data-service)
- **功能**: 健康数据存储和管理
- **端口**: 8005
- **文档**: [health-data-service API](./health-data-service.md)

### 6. 区块链服务 (blockchain-service)
- **功能**: 健康数据区块链存储和验证
- **端口**: 8006
- **文档**: [blockchain-service API](./blockchain-service.md)

### 7. 认证服务 (auth-service)
- **功能**: 用户认证和授权管理
- **端口**: 8007
- **文档**: [auth-service API](./auth-service.md)

### 8. API网关 (api-gateway)
- **功能**: 统一API入口和路由管理
- **端口**: 8000
- **文档**: [api-gateway API](./api-gateway.md)

### 9. RAG知识服务 (rag-service)
- **功能**: 知识检索和生成
- **端口**: 8009
- **文档**: [rag-service API](./rag-service.md)

## 诊断服务群

### 10. 望诊服务 (look-service)
- **功能**: 面部和舌象分析
- **端口**: 8010
- **文档**: [look-service API](./diagnostic-services_look-service.md)

### 11. 闻诊服务 (listen-service)
- **功能**: 语音和呼吸分析
- **端口**: 8011
- **文档**: [listen-service API](./diagnostic-services_listen-service.md)

### 12. 问诊服务 (inquiry-service)
- **功能**: 症状询问和分析
- **端口**: 8012
- **文档**: [inquiry-service API](./diagnostic-services_inquiry-service.md)

### 13. 切诊服务 (palpation-service)
- **功能**: 脉象分析
- **端口**: 8013
- **文档**: [palpation-service API](./diagnostic-services_palpation-service.md)

### 14. 算诊服务 (calculation-service)
- **功能**: 综合诊断计算
- **端口**: 8014
- **文档**: [calculation-service API](./diagnostic-services_calculation-service.md)

## 支撑服务

### 15. 医疗资源服务 (medical-resource-service)
- **功能**: 医疗资源管理
- **端口**: 8015
- **文档**: [medical-resource-service API](./medical-resource-service.md)

### 16. 消息总线 (message-bus)
- **功能**: 服务间消息通信
- **端口**: 8016
- **文档**: [message-bus API](./message-bus.md)

### 17. 用户服务 (user-service)
- **功能**: 用户信息管理
- **端口**: 8017
- **文档**: [user-service API](./user-service.md)

## API 调用流程

```mermaid
graph TD
    A[客户端] --> B[API网关 :8000]
    B --> C[认证服务 :8007]
    B --> D[智能体服务群]
    B --> E[诊断服务群]
    B --> F[业务服务群]

    D --> D1[小艾 :8001]
    D --> D2[小克 :8002]
    D --> D3[老克 :8003]
    D --> D4[索儿 :8004]

    E --> E1[望诊 :8010]
    E --> E2[闻诊 :8011]
    E --> E3[问诊 :8012]
    E --> E4[切诊 :8013]
    E --> E5[算诊 :8014]

    F --> F1[健康数据 :8005]
    F --> F2[区块链 :8006]
    F --> F3[RAG知识 :8009]
```

## 通用规范

### 请求格式
- **Content-Type**: `application/json`
- **认证方式**: `Bearer Token`
- **字符编码**: `UTF-8`

### 响应格式
```json
{
"code": 200,
"message": "success",
"data": {},
"timestamp": "2025-06-06T13:00:00Z"
}
```

### 错误处理
所有服务遵循统一的错误码规范：
- `200`: 成功
- `400`: 请求参数错误
- `401`: 未授权
- `403`: 权限不足
- `404`: 资源不存在
- `500`: 服务器错误

## 开发指南

### 环境配置
```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f [service-name]
```

### 测试工具
- **Postman集合**: [下载链接](./postman/suoke-life-api.json)
- **Swagger UI**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

## 更新日志

- **2025-06-06**: 初始版本发布
- **版本**: v1.0.0
- **维护团队**: 索克生活技术团队

"""

        overview_file = self.docs_dir / "README.md"
        with open(overview_file, 'w', encoding='utf-8') as f:
            f.write(overview_content)

        logger.info(f"✅ API总览文档生成完成: {overview_file}")

def main():
    """主函数"""
    project_root = os.getcwd()

    logger.info("🚀 启动API文档生成器")

    generator = APIDocumentationGenerator(project_root)

    try:
        success = generator.generate_all_docs()

        if success:
            logger.info("🎉 API文档生成完成！")
            logger.info(f"📁 文档目录: {generator.docs_dir}")
            return 0
        else:
            logger.warning("⚠️ 部分API文档生成失败")
            return 1

    except Exception as e:
        logger.error(f"❌ API文档生成失败: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 