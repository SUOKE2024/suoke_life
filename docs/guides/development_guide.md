# SUOKE-LIFE 开发指南

## 目录

1. [开发环境配置](#开发环境配置)
2. [项目结构](#项目结构)
3. [编码规范](#编码规范)
4. [开发流程](#开发流程)
5. [测试规范](#测试规范)
6. [发布流程](#发布流程)

## 开发环境配置

### 必要工具
- Flutter SDK 3.16+
- Android Studio / VS Code
- Git
- Python 3.11+
- PostgreSQL 15+
- Redis 7.0+

### IDE 配置
...

## 项目结构

```
suoke_life/
├── lib/
│   ├── core/           # 核心功能模块
│   ├── features/       # 业务功能模块
│   ├── shared/         # 共享组件
│   └── main.dart       # 入口文件
├── test/              # 测试文件
├── assets/            # 静态资源
├── docs/              # 项目文档
└── server/            # 后端服务
```

## 编码规范

### Dart/Flutter 规范

1. **命名规范**
   - 类名：大驼峰（PascalCase）
   - 变量/方法：小驼峰（camelCase）
   - 常量：大写下划线（UPPER_SNAKE_CASE）

2. **文件组织**
   ```dart
   // 导入顺序
   import 'dart:xxx';           // Dart 核心库
   import 'package:flutter/xxx';// Flutter 库
   import 'package:xxx/xxx';    // 第三方包
   import '../xxx/xxx.dart';    // 项目内部导入
   ```

3. **注释规范**
   ```dart
   /// 类注释使用三斜线
   class MyClass {
     // 普通注释使用双斜线
     void myMethod() {
       /* 多行注释使用星号 */
     }
   }
   ```

### Python 规范

1. **PEP 8 规范**
2. **类型注解**
3. **异常处理**

## 开发流程

1. **分支管理**
   - main：主分支
   - develop：开发分支
   - feature/*：功能分支
   - bugfix/*：修复分支
   - release/*：发布分支

2. **开发流程**
   ```bash
   # 创建功能分支
   git checkout -b feature/new-feature develop
   
   # 开发完成后
   git push origin feature/new-feature
   
   # 创建 Pull Request
   ```

3. **代码审查**
   - 代码风格
   - 业务逻辑
   - 性能考虑
   - 安全考虑

## 测试规范

1. **单元测试**
   ```dart
   void main() {
     group('MyClass Tests', () {
       test('should ...', () {
         // 测试代码
       });
     });
   }
   ```

2. **集成测试**
3. **UI 测试**
4. **性能测试**

## 发布流程

1. **版本号规范**
   - 主版本号.次版本号.修订号 (1.0.0)
   - 遵循语义化版本规范

2. **发布检查清单**
   - [ ] 版本号更新
   - [ ] 更新日志
   - [ ] 测试通过
   - [ ] 文档更新
   - [ ] 性能检查
   - [ ] 安全检查

3. **发布步骤**
   ```bash
   # 创建发布分支
   git checkout -b release/1.0.0 develop
   
   # 版本号更新
   # 测试和修复
   
   # 合并到主分支
   git checkout main
   git merge release/1.0.0
   
   # 打标签
   git tag -a v1.0.0 -m "版本 1.0.0 发布"
   ```

## 附录

### 常用命令
### 常见问题
### 资源链接