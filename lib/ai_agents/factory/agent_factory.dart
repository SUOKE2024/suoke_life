import '../core/agent_microkernel.dart';
import '../core/autonomous_learning_system.dart';
import '../core/security_privacy_framework.dart';
import '../integration/service_integration.dart';
import '../models/ai_agent.dart';

/// AI代理工厂接口
/// 
/// 负责创建和配置不同类型的AI代理
abstract class AgentFactory {
  /// 创建基础AI代理
  Future<AIAgent> createAgent({
    required String id,
    required String name,
    required AIAgentType type,
    required List<AIAgentCapability> capabilities,
  });
  
  /// 创建医学诊断代理
  Future<AIAgent> createMedicalDiagnosisAgent({
    required String id,
    required String name,
    required bool supportTraditionalChinese,
    required bool supportWesternMedicine,
  });
  
  /// 创建健康管理代理
  Future<AIAgent> createHealthManagementAgent({
    required String id,
    required String name,
    required List<String> specializations,
  });
  
  /// 创建知识图谱代理
  Future<AIAgent> createKnowledgeGraphAgent({
    required String id,
    required String name,
    required List<String> knowledgeDomains,
  });
  
  /// 创建供应链代理
  Future<AIAgent> createSupplyChainAgent({
    required String id,
    required String name,
    required String category,
  });
  
  /// 创建服务集成代理
  Future<AIAgent> createServiceIntegrationAgent({
    required String id,
    required String name,
    required ServiceIntegration serviceIntegration,
  });
}

/// 默认AI代理工厂实现
class DefaultAgentFactory implements AgentFactory {
  final AgentMicrokernel _microkernel;
  final AutonomousLearningSystem _learningSystem;
  final SecurityPrivacyFramework _securityFramework;
  final ServiceIntegrationRegistry _serviceRegistry;
  
  /// 构造函数
  DefaultAgentFactory(
    this._microkernel,
    this._learningSystem,
    this._securityFramework,
    this._serviceRegistry,
  );
  
  @override
  Future<AIAgent> createAgent({
    required String id,
    required String name,
    required AIAgentType type,
    required List<AIAgentCapability> capabilities,
  }) async {
    // 创建基础代理
    final agent = BaseAIAgent(
      id: id,
      name: name,
      type: type,
      capabilities: capabilities,
    );
    
    // 将代理注册到微内核
    await _microkernel.registerAgent(agent);
    
    return agent;
  }
  
  @override
  Future<AIAgent> createMedicalDiagnosisAgent({
    required String id,
    required String name,
    required bool supportTraditionalChinese,
    required bool supportWesternMedicine,
  }) async {
    // 定义医学诊断代理的能力
    final capabilities = <AIAgentCapability>[
      AIAgentCapability.textInput,
      AIAgentCapability.textGeneration,
      AIAgentCapability.knowledgeRetrieval,
    ];
    
    // 添加中医或西医的能力
    if (supportTraditionalChinese) {
      capabilities.add(AIAgentCapability.tcmDiagnosis);
    }
    
    if (supportWesternMedicine) {
      capabilities.add(AIAgentCapability.westernMedicineDiagnosis);
    }
    
    // 创建医学诊断代理
    final agent = await createAgent(
      id: id,
      name: name,
      type: AIAgentType.medicalDiagnosis,
      capabilities: capabilities,
    );
    
    // 配置安全设置
    await _securityFramework.configureAgentSecurity(
      agentId: agent.id,
      dataCategories: [DataCategory.health, DataCategory.personal],
      privacyLevel: PrivacyLevel.sensitive,
    );
    
    return agent;
  }
  
  @override
  Future<AIAgent> createHealthManagementAgent({
    required String id,
    required String name,
    required List<String> specializations,
  }) async {
    // 定义健康管理代理的能力
    final capabilities = <AIAgentCapability>[
      AIAgentCapability.textInput,
      AIAgentCapability.textGeneration,
      AIAgentCapability.knowledgeRetrieval,
      AIAgentCapability.healthDataAnalysis,
      AIAgentCapability.recommendation,
    ];
    
    // 创建健康管理代理
    final agent = await createAgent(
      id: id,
      name: name,
      type: AIAgentType.healthManagement,
      capabilities: capabilities,
    );
    
    // 配置安全设置
    await _securityFramework.configureAgentSecurity(
      agentId: agent.id,
      dataCategories: [DataCategory.health, DataCategory.lifestyle],
      privacyLevel: PrivacyLevel.sensitive,
    );
    
    // 配置学习系统
    await _learningSystem.configureAgentLearning(
      agentId: agent.id,
      learningRate: 0.1,
      feedbackEnabled: true,
      personalizedLearning: true,
    );
    
    return agent;
  }
  
  @override
  Future<AIAgent> createKnowledgeGraphAgent({
    required String id,
    required String name,
    required List<String> knowledgeDomains,
  }) async {
    // 定义知识图谱代理的能力
    final capabilities = <AIAgentCapability>[
      AIAgentCapability.textInput,
      AIAgentCapability.textGeneration,
      AIAgentCapability.knowledgeRetrieval,
      AIAgentCapability.knowledgeGraph,
      AIAgentCapability.dataVisualization,
    ];
    
    // 创建知识图谱代理
    final agent = await createAgent(
      id: id,
      name: name,
      type: AIAgentType.knowledgeGraph,
      capabilities: capabilities,
    );
    
    // 配置安全设置
    await _securityFramework.configureAgentSecurity(
      agentId: agent.id,
      dataCategories: [DataCategory.knowledge],
      privacyLevel: PrivacyLevel.public,
    );
    
    return agent;
  }
  
  @override
  Future<AIAgent> createSupplyChainAgent({
    required String id,
    required String name,
    required String category,
  }) async {
    // 定义供应链代理的能力
    final capabilities = <AIAgentCapability>[
      AIAgentCapability.textInput,
      AIAgentCapability.textGeneration,
      AIAgentCapability.knowledgeRetrieval,
      AIAgentCapability.recommendation,
      AIAgentCapability.dataAnalysis,
    ];
    
    // 创建供应链代理
    final agent = await createAgent(
      id: id,
      name: name,
      type: AIAgentType.supplyChain,
      capabilities: capabilities,
    );
    
    // 配置安全设置
    await _securityFramework.configureAgentSecurity(
      agentId: agent.id,
      dataCategories: [DataCategory.commercial],
      privacyLevel: PrivacyLevel.commercial,
    );
    
    return agent;
  }
  
  @override
  Future<AIAgent> createServiceIntegrationAgent({
    required String id,
    required String name,
    required ServiceIntegration serviceIntegration,
  }) async {
    // 定义服务集成代理的能力
    final capabilities = <AIAgentCapability>[
      AIAgentCapability.textInput,
      AIAgentCapability.textGeneration,
      AIAgentCapability.serviceIntegration,
    ];
    
    // 创建服务集成代理
    final agent = await createAgent(
      id: id,
      name: name,
      type: AIAgentType.serviceIntegration,
      capabilities: capabilities,
    );
    
    // 配置安全设置
    await _securityFramework.configureAgentSecurity(
      agentId: agent.id,
      dataCategories: [DataCategory.service],
      privacyLevel: serviceIntegration.config.privacyLevel,
    );
    
    return agent;
  }
} 