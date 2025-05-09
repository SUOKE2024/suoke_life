# 索克生活APP开发规范

## 目录

- [前言与目标](#前言与目标)
- [开发环境设置](#开发环境设置)
- [代码风格规范](#代码风格规范)
- [命名约定](#命名约定)
- [架构原则](#架构原则)
- [UI设计标准](#ui设计标准)
- [文件与目录结构](#文件与目录结构)
- [测试规范](#测试规范)
- [Git工作流与提交规范](#git工作流与提交规范)
- [文档规范](#文档规范)
- [性能与安全指南](#性能与安全指南)
- [应用运行与部署](#应用运行与部署)
- [参考资源](#参考资源)

## 前言与目标

本规范旨在为索克生活APP项目提供统一的开发标准，确保团队协作高效、代码质量可靠、产品体验一致。所有开发人员必须遵循本规范进行开发工作。

## 开发环境设置

### 必要软件安装

1. **Flutter SDK (3.22.0+)**
   ```bash
   git clone https://github.com/flutter/flutter.git -b stable
   export PATH="$PATH:`pwd`/flutter/bin"
   flutter doctor
   ```
   
   Flutter 3.22+主要优势：
   - 改进的性能与内存管理
   - Material 3设计完整支持
   - 改进的国际化支持
   - Impeller渲染引擎支持
   - 更好的平台集成能力

2. **Dart SDK (3.0.0+)**
   - Flutter SDK包含Dart SDK
   
   Dart 3.0+新特性：
   - Records (记录类型)：支持多返回值和命名字段
   - Pattern matching (模式匹配)：更简洁的数据解构
   - Class modifiers：sealed、final、interface、base和mixin类修饰符
   - 改进的空安全支持
   - 增强的类型系统

3. **IDE推荐**
   - Visual Studio Code + Flutter扩展
     - Dart扩展
     - Flutter扩展
     - Awesome Flutter Snippets
     - Riverpod Snippets
     - Flutter Intl
   - Android Studio / IntelliJ IDEA + Flutter插件
     - Dart插件
     - Flutter插件
     - Flutter Riverpod Snippets

4. **Git版本控制**
   - 最新版本的Git (2.40.0+)
   - 推荐GUI工具：GitKraken, Sourcetree或GitHub Desktop

5. **依赖工具**
   - Xcode 15.0+ (Mac开发iOS必备)
   - Android Studio (Android开发必备)
   - CocoaPods (iOS依赖管理)
   - Ruby 3.0+ (CocoaPods依赖)
   - Node.js 18+ (用于一些前端开发工具)

### 项目设置

1. **获取项目代码**
   ```bash
   git clone [项目仓库URL]
   cd suoke_life
   ```

2. **安装项目依赖**
   ```bash
   flutter pub get
   ```

3. **配置环境变量**
   - 复制`.env-example`为`.env`
   - 填写必要的API密钥和配置信息
   
   ```
   # API端点
   API_BASE_URL=https://dev-api.suoke.life
   
   # AI服务配置
   AI_SERVICE_URL=https://ai-dev.suoke.life
   AI_API_KEY=your_api_key_here
   
   # 第三方服务配置
   WECHAT_APP_ID=your_wechat_app_id
   WECHAT_APP_SECRET=your_wechat_app_secret
   ```

4. **构建与运行**

   开发环境：
   ```bash
   flutter run --dart-define=FLAVOR=dev
   ```
   
   测试环境：
   ```bash
   flutter run --dart-define=FLAVOR=staging
   ```
   
   生产环境：
   ```bash
   flutter run --dart-define=FLAVOR=prod
   ```

5. **编辑器配置**
   - 启用Dart Code格式化工具
   - 配置保存时自动格式化
   - 启用Dart分析器和Lint规则
   - 配置代码片段(snippets)
   - 设置EditorConfig插件

### 特定平台设置

#### iOS开发设置
1. 安装最新版Xcode (15.0+)
2. 配置开发者账号
   ```bash
   open ios/Runner.xcworkspace
   ```
   在Xcode中配置签名证书和团队ID

3. 确保CocoaPods正常运行
   ```bash
   cd ios && pod install
   ```

#### Android开发设置
1. 安装Android Studio和必要SDK
2. 创建开发用模拟器或连接真机
3. 配置签名密钥
   ```bash
   keytool -genkey -v -keystore ~/key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias upload
   ```
4. 在`android/key.properties`中配置签名信息

## 代码风格规范

### Dart/Flutter代码风格

- 严格遵循[Dart官方代码风格指南](https://dart.dev/guides/language/effective-dart/style)
- 使用`flutter format`或IDE插件确保代码格式符合标准
- 行宽限制为100个字符
- 使用两个空格缩进
- 使用尾随逗号优化多行参数的格式
- 优先使用`const`构造函数提高性能

### 注释规范

- 类、公共方法和公共属性必须添加文档注释`///`
- 复杂逻辑必须添加实现注释`//`解释原理
- 避免无意义注释和注释代码
- 文档注释应使用完整的句子并包含参数说明

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

### 代码组织

- 遵循相关性原则组织代码，相关功能应靠近
- 导入语句按以下顺序组织：
  1. Dart官方库
  2. Flutter官方库
  3. 第三方库
  4. 项目内相对路径导入
- 每个分组间用空行分隔
- 保持文件合理大小，单个文件不应超过500行代码

### 语法与特性使用

- 优先使用Dart 3.0+新特性，如模式匹配、记录类型(Records)和密封类(Sealed classes)
- 使用异步编程最佳实践：
  - 适当处理所有Future，使用`async/await`
  - 错误处理必须包含try-catch逻辑
  - 避免在构造函数中使用异步代码
- 避免使用`dynamic`类型，优先使用明确的类型声明
- 优先使用扩展方法提高代码可读性

## 命名约定

### 通用命名原则

- 所有命名应有实际含义，避免缩写和模糊命名
- 优先使用领域术语，确保概念一致性
- 保持命名的长度合理，既表达清晰又简洁
- 避免使用中医、医学领域外的人不易理解的专业术语

### 类与文件命名

- 类名：使用大驼峰命名法（PascalCase），例如`BodyConstitutionAnalyzer`
- 文件名：使用小蛇形命名法（snake_case），例如`body_constitution_analyzer.dart`
- 文件名应与文件中主要类名对应，例如`BodyConstitutionAnalyzer`类应在`body_constitution_analyzer.dart`中
- 页面组件使用`_screen`或`_page`后缀，例如`health_assessment_screen.dart`
- 组件使用`_widget`后缀，例如`tongue_analysis_widget.dart`
- 模型使用`_model`或领域名称，例如`user_model.dart`、`constitution.dart`

### 变量与函数命名

- 变量和函数名：使用小驼峰命名法（camelCase），例如`tongueImage`
- 布尔变量使用`is`、`has`、`should`等前缀，例如`isValidated`
- 常量使用全大写下划线分隔，例如`MAX_RETRY_COUNT`
- 私有成员使用下划线前缀，例如`_privateMethod`
- 函数名应使用动词开头，明确表达行为，例如`calculateScore`、`fetchUserData`

### 中医专有名词命名规范

- 中医体质类型：使用标准化英文术语，例如`PhlegmDampnessType`对应"痰湿质"
- 四诊相关功能：使用标准前缀
  - `look_`前缀对应望诊相关
  - `listen_`前缀对应闻诊相关
  - `inquiry_`前缀对应问诊相关
  - `pulse_`前缀对应切诊相关
- 穴位和经络命名：使用标准拼音全称，例如`zusanli`对应"足三里"

## 架构原则

### 整体架构指导原则

- 严格遵循Clean Architecture + MVVM模式
- 保持关注点分离，UI、业务逻辑与数据层清晰隔离
- 遵循依赖倒置原则，核心业务逻辑不依赖具体实现
- 通过接口而非实现进行交互
- 保持各层独立可测试

### 分层架构规范

- **表现层（Presentation Layer）**
  - 仅包含UI相关代码和视图模型
  - 通过ViewModel暴露状态和行为
  - 视图不应直接访问数据层或领域层

- **领域层（Domain Layer）**
  - 包含业务实体和用例
  - 定义仓库和服务接口
  - 不应包含任何框架特定代码

- **数据层（Data Layer）**
  - 实现领域层定义的仓库接口
  - 处理数据源交互和数据转换
  - 协调缓存和远程数据

- **核心层（Core Layer）**
  - 提供通用工具和服务
  - 定义全局常量和扩展
  - 不依赖于其他任何层

### 智能体架构规范

- 遵循Actor模型设计智能体交互
- 保持四大智能体（小艾、小克、老克、索儿）职责边界清晰
- 智能体通信使用标准化消息格式
- 智能体状态管理遵循单一数据源原则
- 设计松耦合的智能体协作机制，避免紧密依赖

### 依赖注入规范

- 使用Riverpod框架实现依赖注入
- 按功能模块组织Provider
- Provider应声明清晰的依赖关系
- 避免在Provider内部创建其他Provider实例
- 测试时使用ProviderScope进行依赖覆盖

```dart
// Provider示例
final userRepositoryProvider = Provider<UserRepository>((ref) {
  return UserRepositoryImpl(
    remoteDataSource: ref.watch(remoteDataSourceProvider),
    localDataSource: ref.watch(localDataSourceProvider),
  );
});

// ViewModel Provider示例
final userViewModelProvider = StateNotifierProvider<UserViewModel, UserState>((ref) {
  return UserViewModel(
    userRepository: ref.watch(userRepositoryProvider),
    authService: ref.watch(authServiceProvider),
  );
});
```

## UI设计标准

### 设计系统

- 遵循Material Design 3设计规范
- 使用预定义的主题和组件
- 保持视觉元素的一致性
- 颜色使用项目主题定义的颜色
- 所有数值必须使用主题定义的标准值

### 颜色规范

- **主色调**：索克绿 (0xFF35BB78)
- **辅色调**：索克橙 (0xFFFF6800)
- **中性色**：参考Material 3中性色板
- 颜色变量必须从主题中获取，禁止硬编码颜色值

```dart
// 错误示范
Container(color: Color(0xFF35BB78))

// 正确示范
Container(color: Theme.of(context).colorScheme.primary)
```

### 字体与排版

- 使用项目指定的字体系列：PingFang
- 遵循预定义的文本样式和尺寸
- 文本样式应从主题中获取
- 支持动态字体大小以适应辅助功能

```dart
// 正确使用文本样式
Text(
  '体质分析结果',
  style: Theme.of(context).textTheme.titleLarge,
)
```

### 间距与布局

- 遵循8px网格系统
- 统一使用SizedBox或Padding创建间距
- 所有间距值应为8的倍数
- 卡片边距统一使用16px
- 使用响应式布局适配不同屏幕尺寸

### 组件规范

- **卡片**：统一使用16px圆角
- **按钮**：主要按钮使用索克绿，次要按钮使用灰色或透明
- **图标**：优先使用Material图标，自定义图标必须适配深色模式
- **表单**：输入框高度统一，带有清晰的标签和错误提示
- **加载状态**：统一使用项目定义的加载组件

### 中医特色UI元素

- 舌象图展示组件需统一使用`TongueImageViewer`
- 体质雷达图使用`ConstitutionRadarChart`
- 经络穴位图使用`MeridianPointMap`
- 药材展示使用`HerbalItemCard`
- 统一使用中医主题图标集合

### 辅助功能

- 所有UI元素必须支持屏幕阅读器
- 确保足够的颜色对比度（满足WCAG AA级别）
- 支持大字体和高对比度模式
- 提供替代文本描述图像内容
- 导盲与手语识别服务必须覆盖所有关键功能

## 文件与目录结构

### 代码目录组织

严格遵循项目定义的目录结构，主要分为：

```
lib/
├── ai_agents/                  # AI代理相关功能
├── core/                       # 核心工具和常量
├── data/                       # 数据层
├── di/                         # 依赖注入
├── domain/                     # 领域层
├── presentation/               # 表现层
├── app.dart                    # 应用程序入口
└── main.dart                   # 主函数
```

### 模块划分规范

- 按领域功能划分子目录，而不是技术类型
- 相关功能应放在同一目录下
- 保持目录层次不超过4层
- 共用组件放入`common`目录
- 每个功能模块应包含所有相关文件（视图、模型、视图模型）

### 资源文件组织

- 图片放在`assets/images/`目录下
- 图标放在`assets/icons/`目录下
- 字体放在`assets/fonts/`目录下
- 配置文件放在`assets/config/`目录下
- 资源子目录应按功能或类型组织

### 特定模块目录规范

#### AI代理模块目录结构

```
ai_agents/
├── config/                 # 配置
├── core/                   # 核心功能
├── models/                 # AI模型
├── rag/                    # RAG相关
├── services/               # 微服务
└── utils/                  # AI工具函数
```

#### 表现层目录结构

```
presentation/
├── auth/                   # 认证页面与身份管理
├── home/                   # 首页（聊天频道）
├── suoke/                  # SUOKE（服务频道）
├── explore/                # 探索页面
├── life/                   # LIFE（健康生活方式）
├── profile/                # 我的（个人设置、系统管理员）
└── common/                 # 通用组件
```

## 测试规范

### 测试覆盖率要求

- 领域层代码测试覆盖率不低于90%
- 数据层代码测试覆盖率不低于80%
- 表现层视图模型测试覆盖率不低于70%
- 核心工具函数测试覆盖率不低于85%
- CI流程中必须包含测试覆盖率检查

### 单元测试规范

- 使用`test`包编写单元测试
- 测试文件与实现文件保持相同的目录结构
- 测试文件命名为`{原文件名}_test.dart`
- 使用`mocktail`进行依赖模拟
- 每个测试函数只测试一个行为或条件

```dart
// 单元测试示例
test('calculateConstitutionScore should return correct scores', () {
  // 准备测试数据
  final bodyData = MockBodyData();
  final medicalHistory = MockMedicalHistory();
  
  // 执行测试
  final result = calculateConstitutionScores(bodyData, medicalHistory);
  
  // 验证结果
  expect(result.length, equals(9));
  expect(result[0], closeTo(0.75, 0.01));
});
```

### Widget测试规范

- 使用`flutter_test`包编写Widget测试
- 测试UI组件的渲染和交互
- 模拟依赖和状态
- 验证UI元素的可见性和属性

```dart
// Widget测试示例
testWidgets('TongueImageViewer显示舌象图片', (WidgetTester tester) async {
  // 构建Widget
  await tester.pumpWidget(MaterialApp(
    home: TongueImageViewer(imageUrl: 'test_image.png'),
  ));
  
  // 验证渲染
  expect(find.byType(Image), findsOneWidget);
});
```

### 集成测试规范

- 使用`integration_test`包编写端到端测试
- 测试关键用户流程
- 测试跨页面交互
- 验证数据持久性和网络请求

```dart
// 集成测试示例
testWidgets('用户登录流程测试', (WidgetTester tester) async {
  app.main();
  await tester.pumpAndSettle();
  
  // 输入用户名和密码
  await tester.enterText(find.byKey(Key('username_field')), 'testuser');
  await tester.enterText(find.byKey(Key('password_field')), 'password123');
  
  // 点击登录按钮
  await tester.tap(find.byKey(Key('login_button')));
  await tester.pumpAndSettle();
  
  // 验证登录成功，跳转到首页
  expect(find.text('欢迎回来'), findsOneWidget);
});
```

### AI模型测试规范

- 设计特定测试集验证AI功能
- 记录模型输入和输出
- 监控关键性能指标（准确率、延迟）
- 利用金标准数据集进行回归测试

## Git工作流与提交规范

### 分支管理

- 采用GitFlow工作流
- `main`分支：稳定的生产代码
- `develop`分支：开发主分支
- `feature/*`分支：新功能开发
- `bugfix/*`分支：bug修复
- `release/*`分支：版本发布准备
- `hotfix/*`分支：生产环境紧急修复

### 提交信息规范

采用Angular风格的提交信息格式：

```
<类型>(范围): <简短描述>

[可选的详细描述]

[可选的问题引用]
```

类型包括：
- `feat`：新功能
- `fix`：Bug修复
- `docs`：文档变更
- `style`：格式变更（不影响代码功能）
- `refactor`：代码重构
- `perf`：性能优化
- `test`：测试相关
- `chore`：构建过程或辅助工具变动

示例：
```
feat(auth): 添加生物识别登录功能

增加指纹和面部识别登录支持，包括：
- 本地认证逻辑
- UI界面适配
- 本地密钥存储

resolves #123
```

### 代码审查

- 所有代码必须通过Pull Request合并
- 至少需要一位团队成员审查并批准
- 代码审查应关注：
  - 功能完整性
  - 代码质量
  - 性能考量
  - 安全风险
  - 测试覆盖率

### 持续集成

- 提交代码自动触发CI流程
- CI必须包含：代码格式检查、静态分析、单元测试
- 仅当CI通过才能合并代码
- 定期执行集成测试和UI测试

## 文档规范

### 代码文档

- 公共API必须添加文档注释
- 文档注释应描述功能、参数、返回值和异常
- 复杂算法需添加实现说明
- 在文档中包含使用示例

### 产品文档

- 新功能开发必须更新产品文档
- API文档使用OpenAPI规范
- 架构文档使用Markdown格式
- 用户手册应包含截图和操作流程

### 开发文档

- `README.md`保持最新状态
- 开发环境搭建步骤必须详细记录
- 技术决策和设计方案需要记录在`docs`目录
- 使用图表辅助表达架构和流程

## 性能与安全指南

### 性能优化准则

- 使用`const`构造器优化重建
- 实现列表惰性加载和分页
- 避免不必要的setState和重建
- 图片资源应优化大小并使用适当格式
- 实现缓存减少网络请求
- 监控并优化启动时间，目标小于2秒

#### 列表性能优化

```dart
// 使用ListView.builder而非ListView
ListView.builder(
  itemCount: items.length,
  itemBuilder: (context, index) {
    return ListTile(
      title: Text(items[index].title),
    );
  },
);
```

### 内存管理

- 大型列表使用`ListView.builder`
- 及时释放不再需要的资源
- 避免内存泄漏，特别是在订阅和监听器中
- 图片缓存策略合理设置最大大小

```dart
// 使用缓存图片
CachedNetworkImage(
  imageUrl: 'https://example.com/image.jpg',
  placeholder: (context, url) => CircularProgressIndicator(),
  errorWidget: (context, url, error) => Icon(Icons.error),
  maxHeightDiskCache: 1024,
  maxWidthDiskCache: 1024,
);
```

### 安全准则

- 敏感数据使用加密存储
- API通信必须使用HTTPS
- 实现适当的身份验证和授权
- 避免在日志中打印敏感信息
- 实施输入验证防止注入攻击
- 定期更新依赖包修复安全漏洞

### AI与隐私保护

- 智能体推理优先在设备端进行
- 用户数据传输前必须脱敏或匿名化
- 实现多级数据权限控制
- 明确获取用户同意后才收集敏感数据
- 提供数据删除和导出功能

## 应用运行与部署

### 环境配置

- 支持开发、测试、生产三种环境
- 使用环境变量控制API端点
- 开发环境启用更详细的日志
- 各环境使用不同的应用ID和签名

```dart
// 环境配置示例
enum Environment {
  development,
  staging,
  production,
}

class AppConfig {
  final Environment environment;
  final String apiBaseUrl;
  final bool enableDetailedLogs;
  
  static AppConfig? _instance;
  
  factory AppConfig({
    required Environment environment,
  }) {
    _instance ??= AppConfig._internal(environment);
    return _instance!;
  }
  
  AppConfig._internal(this.environment)
    : apiBaseUrl = _getApiBaseUrl(environment),
      enableDetailedLogs = environment != Environment.production;
  
  static String _getApiBaseUrl(Environment env) {
    switch (env) {
      case Environment.development:
        return 'https://dev-api.suoke.life';
      case Environment.staging:
        return 'https://staging-api.suoke.life';
      case Environment.production:
        return 'https://api.suoke.life';
    }
  }
}
```

### 版本管理

- 版本号格式：`Major.Minor.Patch`
- 同时维护内部build编号
- 每次发布必须更新版本号
- 明确记录版本变更内容

### 发布流程

- 创建release分支准备发布
- 执行完整的回归测试
- 在测试环境验证通过后推送到生产
- 发布后监控崩溃报告和用户反馈

### 多平台构建

- iOS应用构建注意事项
  - 确保所有权限描述完整
  - 遵循App Store审核指南
  - 测试不同iOS版本兼容性
  
- Android应用构建注意事项
  - 适配不同屏幕分辨率
  - 优化APK/AAB大小
  - 处理设备碎片化问题

## 参考资源

- [Flutter官方风格指南](https://flutter.dev/docs/development/style-guide)
- [Dart Effective指南](https://dart.dev/guides/language/effective-dart)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [MVVM模式](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93viewmodel)
- [Material Design 3](https://m3.material.io)
- [GitFlow工作流](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow)

---

> 本规范将随项目发展不断更新，请定期查看最新版本。最后更新：2024年6月