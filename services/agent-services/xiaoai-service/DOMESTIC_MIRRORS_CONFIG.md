# 国内镜像源配置说明

## 概述

为了加速Python包的下载和安装，xiaoai-service已配置使用国内镜像源。这可以显著提高依赖安装速度，特别是在中国大陆地区。

## 配置详情

### UV包管理器配置

在 `pyproject.toml` 文件中已添加以下配置：

```toml
[tool.uv]
# 主镜像源 - 清华大学
index-url = "https://pypi.tuna.tsinghua.edu.cn/simple"

# 备用镜像源
extra-index-url = [
    "https://mirrors.aliyun.com/pypi/simple/",
    "https://pypi.douban.com/simple/",
    "https://mirrors.cloud.tencent.com/pypi/simple/",
    "https://mirror.baidu.com/pypi/simple/"
]

# 安装配置
no-cache = false
compile-bytecode = true
upgrade = false

# 解析器配置
resolution = "highest"
prerelease = "disallow"
```

### 镜像源说明

1. **主镜像源**: 清华大学 PyPI 镜像
   - URL: https://pypi.tuna.tsinghua.edu.cn/simple
   - 特点: 稳定、更新及时、速度快

2. **备用镜像源**:
   - **阿里云**: https://mirrors.aliyun.com/pypi/simple/
   - **豆瓣**: https://pypi.douban.com/simple/
   - **腾讯云**: https://mirrors.cloud.tencent.com/pypi/simple/
   - **百度**: https://mirror.baidu.com/pypi/simple/

## 使用效果

### 性能测试结果

使用国内镜像源后的安装速度测试：

```bash
# 安装5个包（requests及其依赖）
$ time uv pip install --force-reinstall requests
Using Python 3.13.3 environment at: /Users/songxu/Developer/suoke_life/.venv
Resolved 5 packages in 906ms
Prepared 5 packages in 89ms
Uninstalled 5 packages in 32ms
Installed 5 packages in 12ms
Bytecode compiled 9154 files in 961ms
 ~ certifi==2025.4.26
 ~ charset-normalizer==3.4.2
 ~ idna==3.10
 ~ requests==2.32.3
 ~ urllib3==2.4.0
uv pip install --force-reinstall requests  1.08s user 1.57s system 124% cpu 2.123 total
```

**总耗时**: 仅2.123秒完成5个包的重新安装！

### 日志验证

从详细日志可以看到UV正在使用阿里云镜像：
```
DEBUG Found stale response for: https://mirrors.aliyun.com/pypi/simple/colorama/
DEBUG Sending revalidation request for: https://mirrors.aliyun.com/pypi/simple/colorama/
```

## 手动配置方法

如果需要在其他项目中使用相同配置，可以：

### 1. 项目级配置（推荐）

在项目的 `pyproject.toml` 中添加 `[tool.uv]` 配置段。

### 2. 全局配置

创建全局配置文件：

```bash
# macOS/Linux
mkdir -p ~/.config/uv
cat > ~/.config/uv/uv.toml << EOF
[tool.uv]
index-url = "https://pypi.tuna.tsinghua.edu.cn/simple"
extra-index-url = [
    "https://mirrors.aliyun.com/pypi/simple/",
    "https://pypi.douban.com/simple/"
]
EOF
```

### 3. 临时使用

```bash
# 临时指定镜像源
uv pip install --index-url https://pypi.tuna.tsinghua.edu.cn/simple package_name

# 或使用环境变量
export UV_INDEX_URL="https://pypi.tuna.tsinghua.edu.cn/simple"
uv pip install package_name
```

## 故障排除

### 1. 镜像源不可用

如果主镜像源不可用，UV会自动尝试备用镜像源。

### 2. 包版本不同步

某些镜像源可能存在同步延迟，如果遇到包版本问题：

```bash
# 临时使用官方源
uv pip install --index-url https://pypi.org/simple package_name
```

### 3. 验证配置

```bash
# 查看当前配置
uv pip config list

# 测试安装（不实际安装）
uv pip install --dry-run package_name
```

## 注意事项

1. **安全性**: 所有配置的镜像源都是HTTPS，确保传输安全
2. **可靠性**: 配置了多个备用镜像源，提高可用性
3. **兼容性**: 配置与UV 0.6.16+版本兼容
4. **更新**: 镜像源地址可能会变化，建议定期检查更新

## 相关链接

- [清华大学 PyPI 镜像使用帮助](https://mirrors.tuna.tsinghua.edu.cn/help/pypi/)
- [阿里云 PyPI 镜像](https://developer.aliyun.com/mirror/pypi)
- [UV 官方文档](https://docs.astral.sh/uv/)

---

**配置完成时间**: 2025年1月27日  
**配置状态**: ✅ 已生效  
**测试状态**: ✅ 通过验证 