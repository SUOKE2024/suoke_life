# uv迁移示例 - RAG服务

## 当前状态
```toml
# services/rag-service/pyproject.toml
[tool.poetry]
name = "rag-service"
version = "1.2.0"
# ... poetry配置
```

## 迁移到uv

### 1. 安装uv
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 创建uv项目
```bash
cd services/rag-service
uv init --python 3.11
```

### 3. 迁移依赖
```bash
# 从poetry.lock生成requirements.txt
poetry export -f requirements.txt --output requirements.txt

# 使用uv安装
uv add -r requirements.txt
```

### 4. 更新Dockerfile
```dockerfile
# 替换原有的pip安装
FROM python:3.11-slim

# 安装uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 复制依赖文件
COPY pyproject.toml uv.lock ./

# 安装依赖
RUN uv sync --frozen

# 复制应用代码
COPY . .

# 运行应用
CMD ["uv", "run", "python", "cmd/server/main.py"]
```

### 5. 更新CI/CD
```yaml
# .github/workflows/rag-service.yml
- name: Install uv
  uses: astral-sh/setup-uv@v1
  
- name: Install dependencies
  run: uv sync

- name: Run tests
  run: uv run pytest
```

## 性能对比

### 安装时间对比
- Poetry: ~3-5分钟
- uv: ~30-60秒

### 依赖解析
- Poetry: ~1-2分钟
- uv: ~5-10秒 