# 索克生活APP贡献指南

## 简介

感谢您有兴趣为索克生活APP项目做出贡献！这份文档旨在指导您完成贡献流程，并确保所有代码更改都符合项目的标准和期望。无论您是修复错误、添加新功能还是改进文档，您的贡献都将帮助我们构建更优质的中医健康管理平台。

在开始贡献之前，请确保您已阅读并理解我们的[行为准则](CODE_OF_CONDUCT.md)，该准则适用于所有参与此项目的贡献者。

## 目录

- [开发环境设置](#开发环境设置)
- [代码规范](#代码规范)
- [开发工作流程](#开发工作流程)
- [提交变更](#提交变更)
- [分支策略](#分支策略)
- [测试指南](#测试指南)
- [文档指南](#文档指南)
- [问题与支持](#问题与支持)
- [许可协议](#许可协议)

## 开发环境设置

### 前提条件

在开始开发之前，请确保您的环境中已安装以下工具：

- **Flutter SDK**: 3.22.0 或更高版本
- **Dart**: 3.0.0 或更高版本
- **Git**: 最新版本
- **IDE**: 推荐使用 Visual Studio Code 或 Android Studio，并安装以下插件：
  - Flutter 扩展
  - Dart 扩展
  - Flutter Riverpod Snippets
  - Flutter Intl

### 环境变量

项目依赖于一些环境变量，您需要在开发环境中设置它们：

1. 复制 `.env-example` 文件并重命名为 `.env`
2. 根据注释填写必要的API密钥和配置信息

```bash
cp .env-example .env
# 编辑 .env 文件
```

### 获取源代码

1. Fork仓库到您的GitHub账户
2. 克隆您的Fork到本地

```bash
git clone https://github.com/YOUR-USERNAME/suoke_life.git
cd suoke_life
```

3. 添加上游仓库作为远程源

```bash
git remote add upstream https://github.com/original-owner/suoke_life.git
```

4. 安装依赖项

```bash
flutter pub get
```

5. 验证环境

```bash
flutter doctor
flutter analyze
```

### 模拟器/设备设置

为了有效测试应用，建议您设置多种设备：

- iOS模拟器（对于Mac用户）
- Android模拟器（所有平台）
- 实体设备（用于测试传感器和性能）

## 代码规范

### 遵循索克生活标准

我们的项目遵循严格的代码规范，在[规范文档](/docs/architecture/coding_standards.md)有详细说明。以下是主要规范：

1. **Dart风格**
   - 遵循[Effective Dart](https://dart.dev/guides/language/effective-dart)指南
   - 使用两个空格缩进
   - 行宽限制为100个字符
   - 使用尾随逗号优化多行参数
   - 优先使用`const`构造函数

2. **注释规范**
   - 类和公共API必须添加文档注释(`///`)
   - 复杂逻辑添加实现注释(`//`)
   - 文档注释应使用完整句子

```dart
/// 计算用户体质评分
///
/// [bodyData] 用户身体数据
/// [medicalHistory] 用户病史
/// 
/// 返回九种体质的评分列表，顺序为：平和质、气虚质、阳虚质等
List<double> calculateConstitutionScores(
  BodyData bodyData,
  MedicalHistory medicalHistory,
) {
  // 实现评分计算逻辑
}
```

3. **架构规则**
   - 严格遵循Clean Architecture + MVVM模式
   - 确保关注点分离
   - 通过接口而非实现进行交互
   - 确保每层的独立性和可测试性

4. **命名约定**
   - 类: 大驼峰命名法 (PascalCase)
   - 文件: 小蛇形命名法 (snake_case)
   - 变量/函数: 小驼峰命名法 (camelCase)
   - 常量: 全大写下划线分隔 (UPPER_SNAKE_CASE)
   - 私有成员: 下划线前缀 (_privateMethod)

### 代码检查工具

在提交前，请确保您的代码通过以下检查：

```bash
# 静态分析
flutter analyze

# 格式化代码
flutter format lib/

# 运行测试
flutter test
```

我们的CI系统会自动运行这些检查，不符合标准的PR将不被合并。

## 开发工作流程

### 功能开发流程

1. **需求理解**：确保您理解所需功能或修复的确切要求
2. **任务规划**：将大型功能分解为可管理的任务
3. **架构设计**：对于大型功能，先写出设计文档并获得审核
4. **增量开发**：采用小步骤推进，频繁提交
5. **持续测试**：边开发边测试，确保质量
6. **代码审查**：完成后寻求团队成员审查
7. **文档同步**：更新相关文档
8. **最终集成**：合并到主分支

### 新功能开发指南

1. 确保创建新功能分支
```bash
git checkout -b feature/my-new-feature
```

2. 围绕新功能编写测试
```bash
touch test/features/my_feature_test.dart
# 编写测试用例
```

3. 实现功能
```bash
# 创建所需文件
touch lib/domain/usecases/my_feature_usecase.dart
touch lib/data/repositories/my_feature_repository_impl.dart
touch lib/presentation/my_feature/view_models/my_feature_view_model.dart
touch lib/presentation/my_feature/screens/my_feature_screen.dart
```

4. 添加UI和资源
```bash
# 添加UI组件和资源文件
touch assets/images/my_feature_icon.png
touch lib/presentation/my_feature/widgets/my_feature_widget.dart
```

5. 更新文档
```bash
# 添加功能文档
touch docs/features/my_feature.md
```

## 提交变更

### 提交消息规范

我们使用Angular风格的提交消息格式：

```
<类型>(<范围>): <简短描述>

[可选的详细描述]

[可选的问题引用]
```

类型包括：
- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档变更
- `style`: 代码风格变更（不影响功能）
- `refactor`: 代码重构
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建过程或辅助工具变动

示例：
```
feat(auth): 添加中医师身份认证流程

实现了基于资格证书的中医师身份认证功能，包括：
- 证书拍照上传
- OCR身份信息提取
- 证书有效性验证

关闭 #123
```

### Pull Request流程

1. 确保您的分支是最新的
```bash
git fetch upstream
git rebase upstream/develop
```

2. 将更改推送到您的Fork
```bash
git push origin feature/my-feature
```

3. 在GitHub上创建Pull Request，提供以下信息：
   - 清晰的标题，使用提交消息格式
   - 详细描述您所做的更改
   - 相关问题的引用
   - 任何注意事项或需讨论的点
   - 测试步骤和预期结果

4. 等待代码审查，并根据反馈进行修改
5. 一旦获得批准，您的PR将被合并

## 分支策略

我们使用GitFlow工作流：

- `main`: 稳定的生产代码
- `develop`: 开发主分支，新功能合并到此
- `feature/*`: 新功能开发
- `bugfix/*`: Bug修复
- `release/*`: 版本发布准备
- `hotfix/*`: 生产环境紧急修复

开发流程：
1. 从`develop`创建功能分支
2. 完成功能后，提交PR到`develop`
3. 准备发布时，从`develop`创建`release`分支
4. 修复`release`分支上的问题后，合并到`main`和`develop`
5. 生产问题修复通过`hotfix`分支处理，并同时合并到`main`和`develop`

## 测试指南

### 测试类型

项目需要以下类型的测试：

1. **单元测试**：测试单个类或函数的行为
   - 所有领域层代码需90%+覆盖率
   - 所有数据层实现需80%+覆盖率

2. **Widget测试**：测试UI组件行为
   - 所有可重用Widget需测试
   - 测试不同状态和交互

3. **集成测试**：测试功能模块协同工作
   - 关键用户流程需全流程测试
   - 核心功能需端到端测试

4. **AI智能体测试**：测试智能体行为和协作能力
   - 每个智能体独立能力测试
   - 多智能体协作场景测试

### 测试命名约定

```dart
void main() {
  group('ClassName', () {
    group('methodName', () {
      test('should behave correctly when condition', () {
        // 测试代码
      });
      
      test('should throw exception when invalid input', () {
        // 测试代码
      });
    });
  });
}
```

### 测试资源

- 测试文件放在对应实现文件的同名目录下
- 测试数据放在`test/fixtures`目录下
- 模拟对象使用`mocktail`库创建

## 文档指南

### 文档类型

项目需要维护以下文档：

1. **API文档**：通过Dart文档注释生成
2. **架构文档**：描述系统架构和设计决策
3. **功能文档**：描述功能和用例
4. **用户指南**：面向用户的使用说明
5. **开发指南**：面向开发者的说明
6. **接口文档**：描述系统间接口

### 文档格式

- 使用Markdown格式
- 使用图表清晰表达架构和流程（推荐PlantUML或Mermaid）
- 结构清晰，包含目录
- 更新日期和版本信息

### 文档位置

- API文档：通过代码注释生成
- 其他文档：`/docs`目录，按主题分类

## 问题与支持

### 报告问题

如果您发现bug或有新功能建议：

1. 检查现有issues，避免重复
2. 使用issue模板提交
3. 提供详细步骤、预期结果和实际结果
4. 附上相关截图或日志
5. 标记严重程度和优先级

### 获取支持

如果您在贡献过程中需要帮助：

- 通过issue提问
- 通过dev-support@suokelife.com联系开发团队
- 参加每周开发者会议

## 许可协议

通过贡献代码，您同意您的贡献将根据项目的[MIT许可证](LICENSE)发布。确保您的贡献不违反任何第三方许可或知识产权。

---

再次感谢您对索克生活APP项目的关注和贡献！您的参与将帮助我们构建一个更优秀的中医健康管理平台，让传统中医智慧以现代方式服务更多人群。 