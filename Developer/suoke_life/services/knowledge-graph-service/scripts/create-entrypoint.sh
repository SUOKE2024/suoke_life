#!/bin/bash

# 创建entrypoint.sh脚本
cat > entrypoint.sh << 'EOF'
#!/bin/sh
set -e

# 创建必要的目录
mkdir -p /app/data /app/models /app/tmp

# 运行服务
exec /app/knowledge-graph-service "$@"
EOF

# 添加执行权限
chmod +x entrypoint.sh

echo "✅ entrypoint.sh 已创建并添加执行权限" 