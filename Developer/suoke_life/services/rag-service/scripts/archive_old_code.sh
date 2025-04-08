#!/bin/bash
# 归档旧的Node.js/Python源代码

set -e

echo "=== 开始归档旧代码 ==="

# 创建归档目录
ARCHIVE_DIR="./archived_code"
ARCHIVE_DATE=$(date +"%Y%m%d")
ARCHIVE_PATH="${ARCHIVE_DIR}/${ARCHIVE_DATE}"

mkdir -p ${ARCHIVE_PATH}

# 归档Python源代码
if [ -d "./src" ]; then
  echo "归档Python源代码..."
  cp -r ./src ${ARCHIVE_PATH}/src
  echo "✅ Python源代码已归档到 ${ARCHIVE_PATH}/src"
fi

# 归档Python相关文件
echo "归档Python相关文件..."
for file in requirements.txt mypy.ini .pylintrc test-app.py; do
  if [ -f "./${file}" ]; then
    cp "./${file}" "${ARCHIVE_PATH}/"
    echo "✅ 文件 ${file} 已归档"
  fi
done

# 归档Python Dockerfile
if [ -f "./Dockerfile" ]; then
  echo "归档Python Dockerfile..."
  cp ./Dockerfile ${ARCHIVE_PATH}/Dockerfile.python
  echo "✅ Python Dockerfile已归档到 ${ARCHIVE_PATH}/Dockerfile.python"
fi

# 创建README文件说明归档内容
cat > ${ARCHIVE_PATH}/README.md << EOF
# 归档代码 - ${ARCHIVE_DATE}

此目录包含从Node.js/Python重构到Go之前的RAG服务代码。

## 目录结构
- src/: Python源代码
- Dockerfile.python: Python版本的Dockerfile
- requirements.txt: Python依赖
- 其他配置文件

## 重构说明
此代码已被Go实现替代，新代码位于项目根目录。归档仅作参考保留。

归档日期: $(date)
EOF

echo "✅ 已创建归档说明文件"

# 创建迁移到Go的目录结构
echo "准备迁移到Go..."

# 确保目录存在
mkdir -p mv_script

# 创建迁移脚本
cat > mv_script/move_go_code.sh << EOF
#!/bin/bash
# 迁移Go代码到项目根目录

set -e

echo "=== 开始迁移Go代码 ==="

# 检查目录是否存在
if [ ! -d "./go-src" ]; then
  echo "❌ go-src目录不存在"
  exit 1
fi

# 移动Go代码文件到项目根目录
echo "移动Go源代码..."
cp -r ./go-src/* ./
echo "✅ Go源代码已移动"

# 更新.gitignore
if [ -f "./.gitignore" ]; then
  # 确保.gitignore包含Go相关内容
  if ! grep -q "# Go" ./.gitignore; then
    cat >> ./.gitignore << EOG

# Go
*.exe
*.exe~
*.dll
*.so
*.dylib
*.test
*.out
go.work
vendor/
EOG
    echo "✅ .gitignore已更新，添加了Go相关规则"
  fi
fi

# 更新README，说明代码已迁移到Go
if [ -f "./README.md" ]; then
  # 备份原README
  cp ./README.md ./README.md.bak
  # 添加Go迁移说明
  cat > ./README.md << EOH
# RAG服务 (Go实现)

本项目是索克生活RAG（检索增强生成）服务的Go语言实现版本。原Python/Node.js版本已归档至archived_code目录。

$(cat ./README.md.bak)
EOH
  echo "✅ README.md已更新，添加了Go迁移说明"
fi

echo "=== Go代码迁移完成 ==="
EOF

chmod +x mv_script/move_go_code.sh
echo "✅ 迁移脚本已创建: mv_script/move_go_code.sh"

echo "=== 归档旧代码完成 ==="
echo "请执行以下步骤完成迁移："
echo "1. 运行 ./scripts/archive_old_code.sh 归档旧代码"
echo "2. 删除原Python源代码: rm -rf src requirements.txt mypy.ini .pylintrc test-app.py"
echo "3. 将Go代码移至根目录: ./mv_script/move_go_code.sh"
echo "4. 重命名Dockerfile: mv Dockerfile.go Dockerfile"
echo "5. 设置新脚本执行权限: chmod +x ./scripts/verify_go_deployment.sh"
echo "6. 提交更改到代码库" 