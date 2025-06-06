"""
generate_grpc - 索克生活项目模块
"""

from pathlib import Path
import os
import subprocess
import sys

#!/usr/bin/env python3
"""
生成gRPC代码的脚本
"""

# 获取项目根目录
project_root = Path(__file__).parent.parent
proto_file = project_root / "api" / "grpc" / "message_bus.proto"
output_dir = project_root / "api" / "grpc"

def main():
    """主函数"""
    print(f"正在从 {proto_file} 生成gRPC代码...")
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 构建protoc命令
    cmd = [
        "python", "-m", "grpc_tools.protoc",
        f"--proto_path={proto_file.parent}",
        f"--python_out={output_dir}",
        f"--grpc_python_out={output_dir}",
        str(proto_file.name)
    ]
    
    # 执行命令
    try:
        subprocess.run(cmd, check=True)
        print("gRPC代码生成成功！")
        
        # 修复导入路径
        fix_imports(output_dir / "message_bus_pb2_grpc.py")
        print("已修复导入路径")
    except subprocess.CalledProcessError as e:
        print(f"gRPC代码生成失败: {e}")
        sys.exit(1)

def fix_imports(grpc_file):
    """修复生成的gRPC文件中的导入路径"""
    with open(grpc_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复导入路径
    fixed_content = content.replace(
        'import message_bus_pb2 as message__bus__pb2',
        'from api.grpc import message_bus_pb2 as message__bus__pb2'
    )
    
    with open(grpc_file, 'w', encoding='utf-8') as f:
        f.write(fixed_content)

if __name__ == "__main__":
    main() 