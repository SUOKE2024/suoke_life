# 索克生活开发指南

## 1. 开发环境搭建

### 1.1 基础环境
```bash
# macOS环境
brew install git python3 node flutter

# Linux环境
apt install git python3 nodejs flutter

# 配置Flutter
flutter config --no-analytics
flutter doctor
```

### 1.2 IDE配置
- VS Code
  - Flutter插件
  - Dart插件
  - Python插件
  - Git插件
  - ESLint插件

### 1.3 环境变量
```bash
# 开发环境变量
export SUOKE_ENV=development
export FLASK_ENV=development
export FLUTTER_ENV=development

# API配置
export API_BASE_URL=http://localhost:8000
export API_VERSION=v1

# 数据库配置
export DB_HOST=localhost
export DB_PORT=3306
export DB_NAME=suoke
export DB_USER=root
export DB_PASS=root
```

## 2. 项目结构

### 2.1 前端结构
```
lib/
├── core/              # 核心功能
│   ├── config/        # 配置
│   ├── network/       # 网络
│   ├── storage/       # 存储
│   └── utils/         # 工具
├── features/          # 功能模块
│   ├── assistant/     # 智能助手
│   ├── lifestyle/     # 生活方式
│   └── progress/      # 进度追踪
├── shared/            # 共享组件
│   ├── widgets/       # 通用组件
│   ├── models/        # 数据模型
│   └── services/      # 服务
└── main.dart          # 入口文件
```

### 2.2 后端结构
```
server/
├── api/              # API接口
│   ├── v1/           # API版本
│   └── middlewares/  # 中间件
├── core/             # 核心功能
│   ├── config/       # 配置
│   ├── database/     # 数据库
│   └── utils/        # 工具
├── models/           # 数据模型
├── services/         # 业务服务
└── app.py           # 入口文件
```

## 3. 编码规范

### 3.1 Flutter/Dart规范
```dart
// 命名规范
class UserProfile { ... }  // 类名使用大驼峰
void getUserInfo() { ... } // 方法名使用小驼峰
final String userName;     // 变量名使用小驼峰

// 代码格式化
dart format lib/

// 代码分析
flutter analyze
```

### 3.2 Python规范
```python
# 命名规范
class UserService:        # 类名使用大驼峰
def get_user_info():     # 函数名使用下划线
user_name = "John"       # 变量名使用下划线

# 代码格式化
black server/

# 代码检查
flake8 server/
```

### 3.3 注释规范
```dart
/// Flutter文档注释
/// 使用三斜线进行文档注释
class User {
  /// 用户ID
  final String id;
  
  /// 创建用户
  /// 
  /// [name] 用户名
  /// [email] 邮箱
  User.create(String name, String email);
}
```

```python
"""Python文档注释
使用三引号进行文档注释
"""
class User:
    """用户类
    
    属性:
        id (str): 用户ID
        name (str): 用户名
    """
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name
```

## 4. Git工作流

### 4.1 分支管理
```
分支策略：
main          # 主分支，用于发布
├── develop   # 开发分支
├── feature/* # 功能分支
├── bugfix/*  # 问题修复
└── release/* # 发布分支
```

### 4.2 提交规范
```
提交格式：
<type>(<scope>): <subject>

type:
- feat: 新功能
- fix: 修复问题
- docs: 文档更新
- style: 代码格式
- refactor: 重构
- test: 测试
- chore: 构建

示例：
feat(auth): 添加用户登录功能
fix(ui): 修复按钮样式问题
```

### 4.3 代码审查
```
审查清单：
1. 代码规范
   - 命名规范
   - 格式规范
   - 注释规范

2. 功能完整
   - 功能实现
   - 边界处理
   - 错误处理

3. 测试覆盖
   - 单元测试
   - 集成测试
   - 边界测���
```

## 5. CI/CD流程

### 5.1 持续集成
```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Flutter
        uses: subosito/flutter-action@v2
      - name: Install dependencies
        run: flutter pub get
      - name: Run tests
        run: flutter test
```

### 5.2 持续部署
```yaml
# .github/workflows/cd.yml
name: CD

on:
  push:
    tags: [ 'v*' ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build
        run: flutter build web
      - name: Deploy
        uses: peaceiris/actions-gh-pages@v3
```

## 6. 调试指南

### 6.1 Flutter调试
```dart
// 日志打印
print('Debug: $value');
debugPrint('Debug: $value');

// 断言
assert(user != null, 'User must not be null');

// 性能分析
Timeline.startSync('Operation');
// ... 操作代码
Timeline.finishSync();
```

### 6.2 Python调试
```python
# 日志记录
import logging
logging.debug('Debug: %s', value)

# 断点调试
import pdb; pdb.set_trace()

# 性能分析
import cProfile
cProfile.run('function_name()')
```

## 7. 发布流程

### 7.1 版本管理
```
版本号规则：v主版本.次版本.修订号
示例：v1.2.3

- 主版本：不兼容的API修改
- 次版本：向下兼容的功能性新增
- 修订号：向下兼容的问题修正
```

### 7.2 发布检查
```
发布清单：
1. 版本确认
   - 版本号更新
   - 更新日志
   - API文档

2. 测试验证
   - 单元测试
   - 集成测试
   - 回归测试

3. 资源检查
   - 静态资源
   - 配置文件
   - 环境变量
```

## 8. 常见问题

### 8.1 环境问题
```
问题：Flutter版本不兼容
解决：
1. flutter channel stable
2. flutter upgrade
3. flutter clean
4. flutter pub get

问题：Python依赖冲突
解决：
1. 创建虚拟环境
2. 使用requirements.txt
3. 指定版本号
```

### 8.2 开发问题
```
问题：热重载不生效
解决：
1. 检查代码语法
2. 重启开发服务
3. 清理缓存

问题：API调用失败
解决：
1. 检查网络连接
2. 验证API地址
3. 检查参数格式
4. 查看错误日志
```