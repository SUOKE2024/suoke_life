class ModelManagerService extends GetxService {
  final SubscriptionService _subscriptionService;
  final CacheManagerService _cacheManager;
  final ConfigManagerService _configManager;
  final HealthCheckService _healthCheck;
  
  // 模型配置
  static const Map<SubscriptionPlan, Map<String, dynamic>> _modelConfig = {
    SubscriptionPlan.basic: {
      'allowed_models': ['basic_v1'],
      'max_tokens': 1000,
      'features': ['basic_completion'],
    },
    SubscriptionPlan.pro: {
      'allowed_models': ['basic_v1', 'pro_v1', 'specialized_v1'],
      'max_tokens': 4000,
      'features': ['basic_completion', 'advanced_completion', 'specialized_tasks'],
    },
    SubscriptionPlan.premium: {
      'allowed_models': ['basic_v1', 'pro_v1', 'specialized_v1', 'premium_v1'],
      'max_tokens': 16000,
      'features': ['basic_completion', 'advanced_completion', 'specialized_tasks', 'custom_fine_tuning'],
    },
  };
  
  // 活跃模型缓存
  final Map<String, AIModel> _activeModels = {};
  
  ModelManagerService({
    required SubscriptionService subscriptionService,
    required CacheManagerService cacheManager,
    required ConfigManagerService configManager,
    required HealthCheckService healthCheck,
  })  : _subscriptionService = subscriptionService,
        _cacheManager = cacheManager,
        _configManager = configManager,
        _healthCheck = healthCheck;

  @override
  void onInit() {
    super.onInit();
    _initializeModels();
  }

  // 初始化模型
  Future<void> _initializeModels() async {
    try {
      final plan = await _subscriptionService.getCurrentPlan();
      final allowedModels = _modelConfig[plan]!['allowed_models'] as List<String>;
      
      // 加载模型配置
      for (final modelId in allowedModels) {
        final config = await _configManager.getModelConfig(modelId);
        if (config != null) {
          _activeModels[modelId] = await _loadModel(modelId, config);
        }
      }
      
    } catch (e) {
      debugPrint('模型初始化失败: $e');
    }
  }

  // 获取会话模型
  Future<AIModel> getSessionModel(String sessionId) async {
    final session = await _cacheManager.get('session_$sessionId');
    if (session == null) {
      throw AIException('会话不存在');
    }

    final modelId = session['model_id'] as String;
    return await getModel(modelId);
  }

  // 获取分析模型
  Future<AIModel> getAnalysisModel(String type) async {
    final modelId = await _configManager.getAnalysisModelId(type);
    return await getModel(modelId);
  }

  // 获取指定模型
  Future<AIModel> getModel(String modelId) async {
    // 检查缓存
    final cachedModel = _activeModels[modelId];
    if (cachedModel != null) {
      return cachedModel;
    }

    // 检查权限
    if (!await _canAccessModel(modelId)) {
      throw AIException('无权访问此模型');
    }

    // 加载模型
    final config = await _configManager.getModelConfig(modelId);
    if (config == null) {
      throw AIException('模型配置不存在');
    }

    final model = await _loadModel(modelId, config);
    _activeModels[modelId] = model;
    return model;
  }

  // 检查模型访问权限
  Future<bool> _canAccessModel(String modelId) async {
    final plan = await _subscriptionService.getCurrentPlan();
    final allowedModels = _modelConfig[plan]!['allowed_models'] as List<String>;
    return allowedModels.contains(modelId);
  }

  // 加载模型
  Future<AIModel> _loadModel(
    String modelId,
    Map<String, dynamic> config,
  ) async {
    try {
      // 健康检查
      final health = await _healthCheck.checkModel(modelId);
      if (!health.isHealthy) {
        throw AIException('模型状态异常: ${health.details}');
      }

      return AIModel(
        id: modelId,
        version: config['version'],
        capabilities: config['capabilities'],
        parameters: config['parameters'],
        status: ModelStatus.ready,
      );

    } catch (e) {
      throw AIException('加载模型失败', details: e);
    }
  }

  // 获取模型能力
  Future<Map<String, dynamic>> getModelCapabilities(String modelId) async {
    final model = await getModel(modelId);
    return model.capabilities;
  }

  // 获取可用模型列表
  Future<List<String>> getAvailableModels() async {
    final plan = await _subscriptionService.getCurrentPlan();
    return _modelConfig[plan]!['allowed_models'] as List<String>;
  }

  @override
  void onClose() {
    _activeModels.clear();
    super.onClose();
  }
} 