#!/bin/bash
# 编译所有proto文件到Python代码

# 设置工作目录
cd "$(dirname "$0")/.."

# 确保目标目录存在
mkdir -p api/grpc

# 找出所有的proto文件
PROTO_FILES=$(find api/grpc -name "*.proto")

echo "正在编译以下proto文件:"
for file in $PROTO_FILES; do
  echo " - $file"
done

# 编译proto文件
python -m grpc_tools.protoc \
  --proto_path=api/grpc \
  --python_out=api/grpc \
  --grpc_python_out=api/grpc \
  $PROTO_FILES

# 修复Python导入问题
find api/grpc -name "*_pb2*.py" -type f -exec sed -i.bak -E 's/^import (.+_pb2.*)/from api.grpc import \1/g' {} \;
find api/grpc -name "*.bak" -type f -delete

echo "编译完成！" 