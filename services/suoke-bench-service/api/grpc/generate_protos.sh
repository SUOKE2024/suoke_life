#!/bin/bash

# 生成Python gRPC代码
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. benchmark.proto

# 修复相对导入问题
sed -i '' 's/import benchmark_pb2 as benchmark__pb2/from api.grpc import benchmark_pb2 as benchmark__pb2/g' benchmark_pb2_grpc.py

echo "Proto files generated successfully!"