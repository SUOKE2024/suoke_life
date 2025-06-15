#!/usr/bin/env python
"""
生成gRPC代码的脚本
使用方法: python scripts/generate_proto.py
"""

import os
import subprocess
import sys
from pathlib import Path


def main():
    # 确定项目根目录
    root_dir = Path(__file__).parent.parent
    proto_file = root_dir / "api" / "grpc" / "knowledge.proto"
    output_dir = root_dir / "app" / "api" / "grpc" / "generated"
    
    # 确保输出目录存在
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建__init__.py文件
    init_file = output_dir / "__init__.py"
    if not init_file.exists():
        init_file.touch()
    
    # 构建protoc命令
    cmd = [
        "python", "-m", "grpc_tools.protoc",
        f"--proto_path={proto_file.parent}",
        f"--python_out={output_dir}",
        f"--grpc_python_out={output_dir}",
        str(proto_file)
    ]
    
    print(f"执行命令: {' '.join(cmd)}")
    
    try:
        # 执行protoc命令
        subprocess.check_call(cmd)
        print(f"成功生成gRPC代码到 {output_dir}")
        
        # 修复生成的导入语句
        fix_imports(output_dir)
        
        return 0
    except subprocess.CalledProcessError as e:
        print(f"生成gRPC代码失败: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"发生错误: {e}", file=sys.stderr)
        return 1


def fix_imports(output_dir):
    """修复生成的Python文件中的导入语句"""
    pb2_file = list(output_dir.glob("*_pb2.py"))[0]
    pb2_grpc_file = list(output_dir.glob("*_pb2_grpc.py"))[0]
    
    # 读取并修改pb2_grpc文件
    with open(pb2_grpc_file, "r") as f:
        content = f.read()
    
    # 修改导入语句
    # 例如: import knowledge_pb2 as knowledge__pb2
    # 修改为: from . import knowledge_pb2 as knowledge__pb2
    pb2_basename = pb2_file.stem
    old_import = f"import {pb2_basename} as"
    new_import = f"from . import {pb2_basename} as"
    
    if old_import in content:
        content = content.replace(old_import, new_import)
        
        with open(pb2_grpc_file, "w") as f:
            f.write(content)
        
        print(f"修复了 {pb2_grpc_file} 中的导入语句")


if __name__ == "__main__":
    sys.exit(main()) 