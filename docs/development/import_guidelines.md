# Python导入语句规范指南

## 📋 导入顺序

按照以下顺序组织导入语句：

1. **标准库导入**
2. **第三方库导入**
3. **本地应用导入**

每组之间用空行分隔。

## ✅ 推荐做法

### 1. 使用具体导入
```python
# ✅ 推荐
from typing import List, Dict, Optional
from pathlib import Path

# ❌ 避免
from typing import *
```

### 2. 导入语句分行
```python
# ✅ 推荐 - 多个导入时使用括号分行
from some_module import (
    function_one,
    function_two,
    ClassOne,
    ClassTwo
)

# ❌ 避免 - 过长的单行导入
from some_module import function_one, function_two, ClassOne, ClassTwo, function_three
```

### 3. 模块导入 vs 具体导入
```python
# ✅ 推荐 - 对于常用的大型模块
import os
import sys
import json

# ✅ 推荐 - 对于特定功能
from datetime import datetime, timedelta
from pathlib import Path

# ❌ 避免 - 通配符导入
from os import *
```

### 4. 相对导入
```python
# ✅ 推荐 - 明确的相对导入
from .models import User
from ..utils import helper_function

# ✅ 推荐 - 绝对导入
from src.models import User
from src.utils import helper_function
```

## 🛠️ 工具配置

### isort配置
在 `pyproject.toml` 中配置：
```toml
[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
include_trailing_comma = true
```

### autoflake配置
移除未使用的导入：
```bash
autoflake --in-place --remove-all-unused-imports file.py
```

## 🚫 避免的做法

1. **通配符导入**
   ```python
   # ❌ 避免
   from module import *
   ```

2. **多个模块单行导入**
   ```python
   # ❌ 避免
   import os, sys, json
   ```

3. **未使用的导入**
   ```python
   # ❌ 避免
   import unused_module
   ```

4. **循环导入**
   ```python
   # ❌ 避免
   # file_a.py
   from file_b import something
   
   # file_b.py
   from file_a import something_else
   ```

## 🔧 自动化工具

### 1. 使用isort排序导入
```bash
isort your_file.py
```

### 2. 使用autoflake移除未使用导入
```bash
autoflake --in-place --remove-all-unused-imports your_file.py
```

### 3. 使用black格式化代码
```bash
black your_file.py
```

## 📝 检查清单

在提交代码前检查：

- [ ] 导入语句按正确顺序排列
- [ ] 没有通配符导入
- [ ] 没有未使用的导入
- [ ] 长导入语句已分行
- [ ] 没有循环导入

## 🎯 最佳实践

1. **定期运行导入优化工具**
2. **在CI/CD中集成导入检查**
3. **团队代码审查时关注导入质量**
4. **使用IDE插件自动优化导入**
