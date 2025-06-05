#!/usr/bin/env python3
"""
修复测试文件中的AgentResponse定义
"""

import re
import os

def fix_agent_response_definitions():
    """修复AgentResponse定义"""
    test_files = [
        "test/unit/test_workflow_engine.py"
    ]
    
    for file_path in test_files:
        if not os.path.exists(file_path):
            continue
            
        print(f"修复文件: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修复AgentResponse创建，添加必需字段
        # 1. 成功响应
        content = re.sub(
            r'AgentResponse\(\s*\n\s*success=True,\s*\n\s*data=([^,]+),\s*\n\s*error=None,\s*\n\s*execution_time=([^,]+),\s*\n\s*timestamp=([^,]+),\s*\n\s*\)',
            r'AgentResponse(\n            success=True,\n            data=\1,\n            error=None,\n            agent_id="test_agent",\n            request_id="test_request",\n            execution_time=\2,\n            timestamp=\3,\n        )',
            content
        )
        
        # 2. 失败响应
        content = re.sub(
            r'AgentResponse\(\s*\n\s*success=False,\s*\n\s*data=([^,]+),\s*\n\s*error=([^,]+),\s*\n\s*execution_time=([^,]+),\s*\n\s*timestamp=([^,]+),\s*\n\s*\)',
            r'AgentResponse(\n                success=False,\n                data=\1,\n                error=\2,\n                agent_id="test_agent",\n                request_id="test_request",\n                execution_time=\3,\n                timestamp=\4,\n            )',
            content
        )
        
        # 3. 修复mock_send_request函数中的返回值
        content = re.sub(
            r'return AgentResponse\(\s*\n\s*success=True,\s*\n\s*data=\{"result": f"success from \{request\.agent_id\}"\},\s*\n\s*error=None,\s*\n\s*execution_time=([^,]+),\s*\n\s*timestamp=([^,]+),\s*\n\s*\)',
            r'return AgentResponse(\n                success=True,\n                data={"result": f"success from {request.agent_id}"},\n                error=None,\n                agent_id=request.agent_id,\n                request_id=request.request_id,\n                execution_time=\1,\n                timestamp=\2,\n            )',
            content
        )
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 修复完成: {file_path}")

if __name__ == "__main__":
    fix_agent_response_definitions()
    print("🎉 所有AgentResponse修复完成！") 