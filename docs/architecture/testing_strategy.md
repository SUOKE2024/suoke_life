# 索克生活APP测试策略

## 简介

本文档定义了索克生活APP项目的测试策略，旨在确保应用的质量、可靠性和可维护性。测试策略覆盖从单元测试到端到端测试的全方位测试方法，特别关注AI智能体系统和中医健康功能模块的测试需求。

索克生活作为融合传统中医与现代技术的健康管理平台，对软件质量有着极高要求。本策略设计确保了关键健康功能的准确性、AI系统的可靠性、数据安全和隐私保护，以及出色的用户体验。

## 测试目标与原则

### 核心测试目标

1. **功能完整性**：确保所有功能按照需求正确实现
2. **AI可靠性**：验证智能体系统在各种条件下的表现符合预期
3. **数据准确性**：确保健康数据处理和分析结果的准确性
4. **安全性**：验证隐私保护机制和数据安全控制
5. **性能表现**：确保应用在各种设备上保持流畅体验
6. **可用性**：验证应用符合可访问性标准并提供良好用户体验

### 指导原则

- **测试先行**：采用测试驱动开发(TDD)方法，先编写测试再实现功能
- **自动化优先**：尽可能实现测试自动化，减少手动测试工作
- **持续测试**：将测试集成到CI/CD流程，实现早期发现问题
- **独立性**：测试应独立运行，不依赖外部系统或特定环境
- **全面覆盖**：确保各层架构和功能点都有适当测试覆盖
- **仿真数据**：使用符合中医特点的仿真数据测试AI功能
- **边界测试**：充分测试边界条件和异常情况
- **安全意识**：将安全性测试视为必要环节，而非附加项

## 测试类型与范围

### 1. 单元测试 (Unit Tests)

单元测试针对独立组件（类、函数、方法）进行测试，验证其在隔离状态下的行为。

#### 范围与目标

- **领域层**：所有实体、用例和领域服务
- **数据层**：存储库实现、数据模型和映射器
- **工具和辅助类**：核心层的工具函数和通用组件
- **ViewModels**：视图模型的业务逻辑和状态转换

#### 覆盖率目标

| 模块类型 | 最低行覆盖率 | 最低分支覆盖率 |
|---------|------------|--------------|
| 领域层   | 90%        | 85%          |
| 数据层   | 80%        | 75%          |
| 核心工具 | 85%        | 80%          |
| 视图模型 | 75%        | 70%          |

#### 测试框架与工具

- **主要框架**：`flutter_test`、`test`
- **模拟框架**：`mocktail`
- **覆盖率工具**：`flutter test --coverage`

#### 示例

```dart
group('ConstitutionAnalyzer', () {
  late ConstitutionAnalyzer analyzer;
  late MockSymptomRepository symptomRepository;
  
  setUp(() {
    symptomRepository = MockSymptomRepository();
    analyzer = ConstitutionAnalyzer(symptomRepository: symptomRepository);
  });
  
  test('should calculate phlegm-dampness score correctly when symptoms match', () {
    // Arrange
    final symptoms = [
      Symptom(id: 1, name: '肢体困重', category: 'phlegm-dampness', weight: 0.8),
      Symptom(id: 2, name: '痰多', category: 'phlegm-dampness', weight: 0.9),
    ];
    
    when(() => symptomRepository.getSymptomsByCategory('phlegm-dampness'))
        .thenReturn(symptoms);
    
    final userSymptoms = {'肢体困重': 4, '痰多': 5}; // 1-5 scale
    
    // Act
    final score = analyzer.calculateCategoryScore('phlegm-dampness', userSymptoms);
    
    // Assert
    expect(score, closeTo(0.76, 0.01)); // (0.8*4/5 + 0.9*5/5)/2 = 0.76
    verify(() => symptomRepository.getSymptomsByCategory('phlegm-dampness')).called(1);
  });
  
  test('should throw exception when category is invalid', () {
    // Arrange
    when(() => symptomRepository.getSymptomsByCategory('invalid-category'))
        .thenReturn([]);
    
    // Act & Assert
    expect(
      () => analyzer.calculateCategoryScore('invalid-category', {}),
      throwsA(isA<InvalidCategoryException>())
    );
  });
});
```

### 2. 组件测试 (Widget Tests)

组件测试验证UI组件的渲染、交互和状态变化行为。

#### 范围与目标

- **可重用组件**：所有共享UI组件
- **复杂视图**：包含业务逻辑的屏幕
- **智能体界面**：智能体交互组件
- **数据可视化**：图表和数据展示组件

#### 覆盖率目标

| 组件类型     | 最低覆盖率 |
|------------|----------|
| 核心UI组件   | 80%      |
| 屏幕页面     | 60%      |
| 可视化组件   | 70%      |

#### 测试框架与工具

- **主要框架**：`flutter_test`(Widget Testing)
- **助手工具**：`golden_toolkit`(视觉回归测试)
- **UI模拟工具**：`network_image_mock`

#### 示例

```dart
group('TongueImageAnalysisWidget', () {
  testWidgets('should display loading indicator when analysis is in progress', (WidgetTester tester) async {
    // Arrange
    final mockViewModel = MockTongueAnalysisViewModel();
    when(() => mockViewModel.analysisState).thenReturn(AnalysisState.loading);
    when(() => mockViewModel.tongueImage).thenReturn(null);
    
    // Act
    await tester.pumpWidget(
      MaterialApp(
        home: ChangeNotifierProvider<TongueAnalysisViewModel>.value(
          value: mockViewModel,
          child: TongueImageAnalysisWidget(),
        ),
      ),
    );
    
    // Assert
    expect(find.byType(CircularProgressIndicator), findsOneWidget);
    expect(find.text('正在分析舌象...'), findsOneWidget);
    expect(find.byType(TongueAnalysisResultCard), findsNothing);
  });
  
  testWidgets('should display analysis results when available', (WidgetTester tester) async {
    // Arrange
    final mockViewModel = MockTongueAnalysisViewModel();
    final mockAnalysisResult = TongueAnalysisResult(
      tongueColor: '淡红',
      tongueShape: '正常',
      tongueCoating: '薄白',
      relatedConstitution: '气虚质',
      confidence: 0.85,
    );
    
    when(() => mockViewModel.analysisState).thenReturn(AnalysisState.completed);
    when(() => mockViewModel.tongueImage).thenReturn(Uint8List(0)); // Mock image
    when(() => mockViewModel.analysisResult).thenReturn(mockAnalysisResult);
    
    // Act
    await tester.pumpWidget(
      MaterialApp(
        home: ChangeNotifierProvider<TongueAnalysisViewModel>.value(
          value: mockViewModel,
          child: TongueImageAnalysisWidget(),
        ),
      ),
    );
    
    // Assert
    expect(find.byType(TongueAnalysisResultCard), findsOneWidget);
    expect(find.text('淡红'), findsOneWidget);
    expect(find.text('气虚质'), findsOneWidget);
    expect(find.byType(CircularProgressIndicator), findsNothing);
  });
});
```

### 3. 集成测试 (Integration Tests)

集成测试验证多个组件或子系统协同工作的能力，确保不同模块的正确集成。

#### 范围与目标

- **用户流程**：完整用户流程和关键功能路径
- **数据流**：从UI到数据层的端到端数据流
- **网络交互**：API交互和数据同步流程
- **数据存储**：数据持久化和检索流程

#### 优先测试场景

1. 用户注册与身份认证流程
2. 四诊数据采集与分析流程
3. 健康报告生成与查看流程
4. 预约与服务购买流程
5. 系统设置与隐私管理流程

#### 测试框架与工具

- **主要框架**：`integration_test`
- **网络模拟**：`mockito`、`http_mock_adapter`
- **数据库测试**：`sqflite_common_ffi`

#### 示例

```dart
void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();
  
  group('End-to-end health assessment flow', () {
    testWidgets('Complete health assessment and view results', (tester) async {
      // Start app
      app.main();
      await tester.pumpAndSettle();
      
      // Login (assuming we have a test account)
      await tester.tap(find.byKey(Key('loginButton')));
      await tester.pumpAndSettle();
      await tester.enterText(find.byKey(Key('emailField')), 'test@example.com');
      await tester.enterText(find.byKey(Key('passwordField')), 'password123');
      await tester.tap(find.byKey(Key('submitLoginButton')));
      await tester.pumpAndSettle();
      
      // Navigate to health assessment
      await tester.tap(find.byKey(Key('healthAssessmentTile')));
      await tester.pumpAndSettle();
      
      // Complete tongue analysis section
      await tester.tap(find.byKey(Key('tongueAnalysisCard')));
      await tester.pumpAndSettle();
      await tester.tap(find.byKey(Key('uploadTongueImageButton')));
      await tester.pumpAndSettle();
      // Simulate image selection
      await simulateImageSelection(tester, 'test_assets/sample_tongue.jpg');
      await tester.pumpAndSettle(Duration(seconds: 3)); // Wait for analysis
      await tester.tap(find.byKey(Key('confirmTongueAnalysisButton')));
      await tester.pumpAndSettle();
      
      // Complete questionnaire
      await fillHealthQuestionnaire(tester);
      await tester.tap(find.byKey(Key('submitQuestionnaireButton')));
      await tester.pumpAndSettle(Duration(seconds: 2));
      
      // View results
      expect(find.text('体质分析报告'), findsOneWidget);
      expect(find.byKey(Key('constitutionRadarChart')), findsOneWidget);
      expect(find.byKey(Key('healthRecommendationsCard')), findsOneWidget);
      
      // Verify data persistence
      await tester.tap(find.byIcon(Icons.home));
      await tester.pumpAndSettle();
      await tester.tap(find.byKey(Key('historyButton')));
      await tester.pumpAndSettle();
      
      expect(find.textContaining('体质评估'), findsOneWidget);
      expect(find.textContaining(DateTime.now().toString().substring(0, 10)), findsOneWidget);
    });
  });
}

Future<void> fillHealthQuestionnaire(WidgetTester tester) async {
  // Simplified questionnaire completion
  final questions = await tester.widgetList(find.byType(QuestionCard)).toList();
  for (int i = 0; i < questions.length; i++) {
    await tester.tap(find.byKey(Key('ratingOption_4')).at(i));
    await tester.pumpAndSettle();
  }
}

Future<void> simulateImageSelection(WidgetTester tester, String assetPath) async {
  // Implementation depends on how image picking is mocked in tests
}
```

### 4. AI智能体测试 (AI Agent Tests)

专门测试AI智能体系统的功能、交互和决策能力。

#### 范围与目标

- **智能体基础能力**：验证每个智能体的专业能力
- **多智能体协作**：测试智能体间的协作能力
- **对话管理**：验证对话流程和上下文维护
- **推理准确性**：测试AI推理结果的准确性
- **弹性与鲁棒性**：验证在异常输入下的表现

#### 测试方法

1. **模拟对话测试**：使用预设对话脚本测试智能体反应
2. **场景模拟测试**：模拟完整用户场景和交互流程
3. **压力测试**：测试高负载下的性能和稳定性
4. **对抗测试**：使用边界情况和异常输入测试系统鲁棒性
5. **A/B测试**：比较不同版本智能体的表现

#### 测试框架与工具

- **对话测试框架**：自研AI测试框架
- **模拟数据生成**：`fake_data_generator`
- **评估工具**：智能体评分系统

#### 示例

```dart
class AgentTestSession {
  final String sessionId;
  final Agent agent;
  final TestEnvironment environment;
  final List<AgentInteraction> interactions = [];
  
  AgentTestSession({
    required this.sessionId,
    required this.agent,
    required this.environment,
  });
  
  Future<AgentResponse> sendQuery(String query, {Map<String, dynamic>? context}) async {
    final agentQuery = AgentQuery(
      sourceId: 'test_user',
      content: query,
      context: context ?? {},
      timestamp: DateTime.now(),
    );
    
    final startTime = DateTime.now();
    final response = await agent.processQuery(agentQuery);
    final endTime = DateTime.now();
    
    interactions.add(AgentInteraction(
      query: agentQuery,
      response: response,
      processingTime: endTime.difference(startTime),
    ));
    
    return response;
  }
  
  AgentTestReport generateReport() {
    return AgentTestReport(
      sessionId: sessionId,
      agentId: agent.id,
      interactions: interactions,
      metrics: _calculateMetrics(),
      timestamp: DateTime.now(),
    );
  }
  
  AgentTestMetrics _calculateMetrics() {
    // Calculate response accuracy, relevance, etc.
    // ...
  }
}

group('XiaoAi Agent Tests', () {
  late MockAgentEnvironment environment;
  late XiaoAiAgent agent;
  
  setUp(() {
    environment = MockAgentEnvironment();
    agent = XiaoAiAgent(
      agentId: 'test_xiaoai',
      services: MockServiceRegistry(),
      environment: environment,
    );
    
    // Initialize agent with test models
    agent.initialize(useTestModels: true);
  });
  
  test('should correctly identify and respond to tongue diagnosis queries', () async {
    // Arrange
    final testSession = AgentTestSession(
      sessionId: 'test_session_001',
      agent: agent,
      environment: environment,
    );
    
    // Simulate user uploading tongue image
    environment.mockTongueImageData(
      imagePath: 'test_assets/tongue_images/pale_red_tongue.jpg',
      expectedAnalysis: TongueAnalysis(
        color: '淡红舌',
        coating: '薄白苔',
        shape: '齿痕舌',
        moisture: '湿润',
        confidence: 0.87,
      ),
    );
    
    // Act
    final response1 = await testSession.sendQuery("我想分析一下我的舌象，帮我看看我的体质");
    final response2 = await testSession.sendQuery("我已经上传了舌头照片，请分析");
    
    // Assert
    expect(response1.intent, equals(AgentIntent.requestImage));
    expect(response1.content, contains("请上传您的舌头照片"));
    
    expect(response2.intent, equals(AgentIntent.analyzeResult));
    expect(response2.content, contains("淡红舌"));
    expect(response2.content, contains("薄白苔"));
    expect(response2.content, contains("气虚")); // Expected constitution inference
    
    expect(response2.suggestions, isNotEmpty);
    expect(response2.suggestions.first, contains("建议增强脾胃功能"));
    
    // Generate test report
    final report = testSession.generateReport();
    expect(report.metrics.relevanceScore, greaterThan(0.8));
    expect(report.metrics.accuracyScore, greaterThan(0.85));
  });
  
  test('should maintain context across multiple interactions', () async {
    // Test context maintenance across conversation
    // ...
  });
  
  test('should handle invalid or unclear user requests gracefully', () async {
    // Test error handling and clarification requests
    // ...
  });
});
```

### 5. 端到端测试 (End-to-End Tests)

端到端测试验证完整应用在真实或近似真实环境中的行为。

#### 范围与目标

- **核心用户旅程**：验证关键用户流程端到端能力
- **设备兼容性**：测试不同设备和操作系统版本上的行为
- **网络场景**：测试不同网络条件下的应用表现
- **离线功能**：验证离线模式下的核心功能可用性

#### 优先测试场景

1. 新用户注册到完成健康评估的端到端流程
2. 从健康评估到获取个性化建议的完整流程
3. 线上预约专家到完成服务的完整流程

#### 测试框架与工具

- **主要框架**：`integration_test` + 设备云平台
- **设备云**：Firebase Test Lab、AWS Device Farm
- **监控工具**：自定义度量收集和性能监控

### 6. 性能测试 (Performance Tests)

性能测试评估应用在各种条件下的响应速度、资源使用和稳定性。

#### 范围与目标

- **启动时间**：测量冷启动和热启动时间
- **UI响应性**：测量UI交互的响应时间
- **资源使用**：监控内存、CPU和电池使用情况
- **网络性能**：测量网络请求完成时间和成功率
- **大数据集**：测试大量数据下的性能表现

#### 性能指标与目标

| 性能指标 | 目标值 |
|---------|-------|
| 冷启动时间 | < 2秒 |
| 热启动时间 | < 0.5秒 |
| 页面过渡时间 | < 300ms |
| 内存峰值 | < 200MB |
| 60 FPS保持率 | > 95% |
| API响应时间 | < 1秒 |
| 舌象分析时间 | < 3秒 |
| 体质计算时间 | < 1秒 |

#### 测试工具与方法

- **性能追踪**：Flutter DevTools、Timeline
- **内存分析**：Flutter Memory Profiler
- **帧率监控**：自定义FPS计数器
- **自动化工具**：AppMetrica、Firebase Performance

### 7. 安全测试 (Security Tests)

安全测试评估应用的数据保护能力和抵御常见安全威胁的能力。

#### 范围与目标

- **数据加密**：验证敏感数据加密实现
- **认证机制**：测试身份验证和授权控制
- **输入验证**：测试对恶意输入的防护能力
- **通信安全**：验证网络通信的安全性
- **数据泄露**：测试防止数据意外泄露的控制措施

#### 安全测试方法

1. **静态分析**：使用静态代码分析工具识别安全漏洞
2. **依赖审查**：定期检查和更新有安全风险的依赖
3. **漏洞扫描**：使用自动化工具扫描常见漏洞
4. **渗透测试**：模拟攻击者的行为测试系统防御能力

#### 关键安全测试领域

- 隐私敏感健康数据的存储和传输
- 个人身份信息(PII)的处理
- 智能体访问控制机制
- 支付处理流程安全
- 用户会话管理

## 测试环境与基础设施

### 测试环境

#### 1. 开发环境 (Development)
- 开发者本地测试环境
- 单元测试和基本集成测试
- 模拟后端和依赖

#### 2. 集成环境 (Integration)
- 共享测试环境
- 集成测试和端到端测试
- 集成测试版本的后端服务
- 测试数据库

#### 3. 预发布环境 (Staging)
- 生产环境的镜像
- 全面的端到端测试
- 性能和负载测试
- 沙盒第三方服务

#### 4. 生产环境 (Production)
- 生产监控和回归测试
- A/B测试
- 金丝雀发布测试

### 测试数据管理

#### 测试数据策略

1. **模拟数据**：符合中医特征的模拟健康数据
2. **匿名化数据**：基于真实数据但已匿名化的测试数据
3. **边界数据**：测试系统边界的特殊数据集
4. **负面测试数据**：设计用于触发错误条件的数据

#### 数据集管理流程

- 测试数据版本控制
- 自动化测试数据生成
- 环境特定数据隔离
- 敏感数据处理控制

## 测试流程与集成

### 开发流程集成

#### 本地开发测试流程

1. 开发者运行单元测试和组件测试
2. 本地运行静态分析和代码格式检查
3. 本地运行关键集成测试
4. 提交代码到版本控制

#### CI流程

1. 触发构建和基本静态分析
2. 运行全套单元测试和组件测试
3. 构建测试版本并部署到测试环境
4. 运行集成测试和端到端测试
5. 运行性能基准测试
6. 生成测试报告

### 测试自动化

#### 自动化范围

- 单元测试和组件测试 (100%)
- 关键集成测试 (90%)
- 端到端测试关键流程 (70%)
- 安全和性能基准测试 (50%)

#### 自动化工具链

- GitHub Actions / Jenkins 持续集成
- Test Lab 设备测试
- 自动化测试报告生成
- 测试结果推送和通知系统

## 测试管理与监控

### 测试指标与KPI

#### 质量指标

- 单元测试覆盖率
- 缺陷逃逸率
- 平均解决时间
- 回归缺陷率
- 用户报告问题率

#### 目标KPI

| 指标 | 目标值 |
|-----|-------|
| 单元测试覆盖率 | > 80% |
| 缺陷逃逸率 | < 5% |
| 严重缺陷数 | 0 |
| 回归缺陷率 | < 2% |
| 发布阻断缺陷 | 0 |

### 缺陷管理流程

1. **缺陷报告**：记录详细步骤、预期结果、实际结果
2. **分类与优先级**：设置严重性和优先级
3. **分配与跟踪**：分配给责任人并跟踪进度
4. **验证与关闭**：验证修复并关闭缺陷

#### 缺陷严重性分类

- **阻断(Blocker)**：阻止功能使用，无法继续测试
- **严重(Critical)**：主要功能失效，但有替代方案
- **主要(Major)**：功能部分受损但可使用
- **次要(Minor)**：小问题，不影响核心功能
- **轻微(Trivial)**：UI细节或改进建议

## 专项测试策略

### 可访问性测试

- 屏幕阅读器兼容性
- 颜色对比度合规
- 键盘导航支持
- 动态字体大小支持
- 符合WCAG AA级标准

### 国际化测试

- 中文(简体/繁体)完整支持
- 英文基础支持
- 日期、货币、数字格式
- 文本扩展与缩短适应性
- RTL语言布局预留

### AI特定测试

- 对抗性测试
- 模型漂移检测
- 信息准确性评估
- 边缘计算功能测试
- 模型更新流程测试

### 中医知识验证

- 中医理论一致性检查
- 诊断推理准确性评估
- 处方建议安全性验证
- 专家审核流程

## 实施与维护

### 测试策略实施计划

1. **初始阶段**：搭建基础框架和自动化基础设施
   - 单元测试框架配置
   - CI集成设置
   - 基本测试数据集建立

2. **增强阶段**：扩展测试覆盖和深度
   - 智能体测试框架实现
   - 性能测试基线建立
   - 安全测试流程整合

3. **成熟阶段**：测试优化和特殊领域覆盖
   - 测试优化和维护
   - 高级智能体测试场景
   - 端到端测试自动化提升

### 测试策略维护

- 季度测试策略审查
- 基于项目发展调整优先级
- 测试工具和框架更新
- 测试团队技能发展计划

## 附录

### 测试模板与示例

- [单元测试模板](/docs/testing/templates/unit_test_template.dart)
- [组件测试模板](/docs/testing/templates/widget_test_template.dart)
- [集成测试模板](/docs/testing/templates/integration_test_template.dart)
- [智能体测试模板](/docs/testing/templates/agent_test_template.dart)

### 相关文档

- [质量保证计划](/docs/qa/quality_assurance_plan.md)
- [自动化测试指南](/docs/testing/automation_guide.md)
- [测试数据管理策略](/docs/testing/test_data_management.md)
- [缺陷管理流程](/docs/qa/defect_management_process.md)

---

本测试策略文档将随着项目发展持续更新。每个季度将进行一次全面审查，确保测试策略与项目目标和技术发展保持一致。

最后更新日期：2024年6月1日 