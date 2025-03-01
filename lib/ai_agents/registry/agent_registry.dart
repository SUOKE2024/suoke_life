import 'dart:async';
import '../core/agent_microkernel.dart';
import '../factory/agent_factory.dart';
import '../models/ai_agent.dart';

/// 代理注册表接口
/// 
/// 负责管理和维护所有AI代理的注册信息
abstract class AgentRegistry {
  /// 初始化注册表
  Future<void> initialize();
  
  /// 获取所有已注册的代理
  List<AIAgent> getAllAgents();
  
  /// 获取指定类型的代理
  List<AIAgent> getAgentsByType(AIAgentType type);
  
  /// 获取具有指定能力的代理
  List<AIAgent> getAgentsByCapability(AIAgentCapability capability);
  
  /// 根据ID获取代理
  AIAgent? getAgentById(String id);
  
  /// 根据名称获取代理
  AIAgent? getAgentByName(String name);
  
  /// 注册代理
  Future<void> registerAgent(AIAgent agent);
  
  /// 注销代理
  Future<void> unregisterAgent(String agentId);
  
  /// 代理状态变化流
  Stream<AgentStatusChange> get agentStatusStream;
}

/// 代理状态变化
class AgentStatusChange {
  /// 代理ID
  final String agentId;
  
  /// 新状态
  final AgentLifecycleState newState;
  
  /// 构造函数
  AgentStatusChange(this.agentId, this.newState);
}

/// 默认代理注册表实现
class DefaultAgentRegistry implements AgentRegistry {
  final AgentMicrokernel _microkernel;
  final AgentFactory _factory;
  final StreamController<AgentStatusChange> _statusController = StreamController.broadcast();
  
  /// 构造函数
  DefaultAgentRegistry(this._microkernel, this._factory);
  
  @override
  Future<void> initialize() async {
    // 注册标准代理（系统启动时创建的默认代理）
    await _registerStandardAgents();
    
    // 监听代理生命周期状态变化
    _microkernel.addListener(_AgentLifecycleListener(_statusController));
  }
  
  @override
  List<AIAgent> getAllAgents() {
    return _microkernel.findAgents();
  }
  
  @override
  List<AIAgent> getAgentsByType(AIAgentType type) {
    return _microkernel.findAgents(type: type);
  }
  
  @override
  List<AIAgent> getAgentsByCapability(AIAgentCapability capability) {
    return _microkernel.findAgents(capabilities: [capability]);
  }
  
  @override
  AIAgent? getAgentById(String id) {
    return _microkernel.getAgent(id);
  }
  
  @override
  AIAgent? getAgentByName(String name) {
    final agents = _microkernel.findAgents().where((agent) => agent.name == name);
    return agents.isEmpty ? null : agents.first;
  }
  
  @override
  Future<void> registerAgent(AIAgent agent) async {
    await _microkernel.registerAgent(agent);
  }
  
  @override
  Future<void> unregisterAgent(String agentId) async {
    await _microkernel.unregisterAgent(agentId);
  }
  
  @override
  Stream<AgentStatusChange> get agentStatusStream => _statusController.stream;
  
  /// 注册标准代理（系统需要的基本代理）
  Future<void> _registerStandardAgents() async {
    // 1. 创建中医辩证代理
    await _factory.createMedicalDiagnosisAgent(
      id: 'tcm_diagnosis',
      name: '中医辩证代理',
      supportTraditionalChinese: true, 
      supportWesternMedicine: false,
    );
    
    // 2. 创建西医诊断代理
    await _factory.createMedicalDiagnosisAgent(
      id: 'western_diagnosis',
      name: '西医诊断代理',
      supportTraditionalChinese: false, 
      supportWesternMedicine: true,
    );
    
    // 3. 创建营养平衡代理
    await _factory.createHealthManagementAgent(
      id: 'nutrition_agent',
      name: '营养平衡代理',
      specializations: ['nutrition', 'diet', 'food_therapy'],
    );
    
    // 4. 创建运动规划代理
    await _factory.createHealthManagementAgent(
      id: 'exercise_agent',
      name: '运动规划代理',
      specializations: ['exercise', 'fitness', 'physical_activity'],
    );
    
    // 5. 创建中医药理知识代理
    await _factory.createKnowledgeGraphAgent(
      id: 'tcm_knowledge',
      name: '中医药理知识代理',
      knowledgeDomains: ['traditional_chinese_medicine', 'herbology', 'acupuncture'],
    );
    
    // 6. 创建西医临床知识代理
    await _factory.createKnowledgeGraphAgent(
      id: 'western_medicine_knowledge',
      name: '西医临床知识代理',
      knowledgeDomains: ['clinical_medicine', 'pharmacology', 'pathology'],
    );
    
    // 7. 创建有机农产品推荐代理
    await _factory.createSupplyChainAgent(
      id: 'organic_product_agent',
      name: '有机农产品推荐代理',
      category: 'organic_products',
    );
    
    // 8. 创建药膳配方代理
    await _factory.createSupplyChainAgent(
      id: 'medicinal_food_agent',
      name: '药膳配方代理',
      category: 'medicinal_food',
    );
  }
}

/// 代理生命周期监听器
class _AgentLifecycleListener implements AgentMicrokernelListener {
  final StreamController<AgentStatusChange> _controller;
  
  _AgentLifecycleListener(this._controller);
  
  @override
  void onAgentRegistered(AIAgent agent) {
    // 不触发状态变化，因为注册时已经设置了初始状态
  }
  
  @override
  void onAgentStateChanged(String agentId, AgentLifecycleState newState) {
    _controller.add(AgentStatusChange(agentId, newState));
  }
  
  @override
  void onAgentUnregistered(String agentId) {
    _controller.add(AgentStatusChange(agentId, AgentLifecycleState.terminated));
  }
} 