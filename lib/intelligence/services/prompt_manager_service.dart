class PromptManagerService extends GetxService {
  final StorageService _storageService;
  final SecurityManagerService _securityManager;
  final ValidationService _validator;
  final SubscriptionService _subscriptionService;
  
  // 提示词缓存
  final Map<String, Map<String, AIPrompt>> _promptCache = {};
  
  // 提示词配置
  static const Map<SubscriptionPlan, Map<String, dynamic>> _promptConfig = {
    SubscriptionPlan.basic: {
      'max_custom_prompts': 5,
      'max_length': 500,
      'features': {'basic', 'template'},
    },
    SubscriptionPlan.pro: {
      'max_custom_prompts': 20,
      'max_length': 2000,
      'features': {'basic', 'template', 'advanced', 'conditional'},
    },
    SubscriptionPlan.premium: {
      'max_custom_prompts': -1,  // 无限制
      'max_length': 5000,
      'features': {'basic', 'template', 'advanced', 'conditional', 'dynamic'},
    },
  };
  
  PromptManagerService({
    required StorageService storageService,
    required SecurityManagerService securityManager,
    required ValidationService validator,
    required SubscriptionService subscriptionService,
  })  : _storageService = storageService,
        _securityManager = securityManager,
        _validator = validator,
        _subscriptionService = subscriptionService;

  Future<AIPrompt> createPrompt(
    String assistantName,
    String name,
    String content, {
    required String userId,
    PromptType type = PromptType.basic,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      // 验证权限
      if (!_canCreatePrompt(userId)) {
        throw AIException(
          '已达到自定义提示词上限',
          code: 'PROMPT_LIMIT_EXCEEDED',
        );
      }

      // 验证内容
      final validationResult = await _validator.validate(
        content,
        'prompt_content',
        userId: userId,
      );
      if (!validationResult.isValid) {
        throw AIException(
          '提示词内容无效',
          code: 'INVALID_PROMPT_CONTENT',
          details: validationResult.errors,
        );
      }

      // 创建提示词
      final prompt = AIPrompt(
        id: 'prompt_${DateTime.now().millisecondsSinceEpoch}',
        name: name,
        content: validationResult.sanitizedData,
        type: type,
        assistantName: assistantName,
        userId: userId,
        metadata: metadata,
      );

      // 保存提示词
      await _savePrompt(prompt);
      
      // 更新缓���
      _updatePromptCache(prompt);

      return prompt;
    } catch (e) {
      throw AIException(
        '创建提示词失败',
        code: 'CREATE_PROMPT_ERROR',
        details: e,
      );
    }
  }

  Future<AIPrompt> getPrompt(
    String promptId, {
    required String userId,
  }) async {
    try {
      // 检查缓存
      final cached = _getFromCache(promptId, userId);
      if (cached != null) return cached;

      // 从存储获取
      final prompt = await _storageService.getPrompt(promptId);
      if (prompt == null) {
        throw AIException(
          '提示词不存在',
          code: 'PROMPT_NOT_FOUND',
        );
      }

      // 验证访问权限
      if (!_canAccessPrompt(prompt, userId)) {
        throw AIException(
          '无权访问此提示词',
          code: 'PROMPT_ACCESS_DENIED',
        );
      }

      // 更新缓存
      _updatePromptCache(prompt);

      return prompt;
    } catch (e) {
      throw AIException(
        '获取提示词失败',
        code: 'GET_PROMPT_ERROR',
        details: e,
      );
    }
  }

  Future<List<AIPrompt>> getUserPrompts(
    String userId, {
    String? assistantName,
    PromptType? type,
  }) async {
    try {
      return await _storageService.getUserPrompts(
        userId,
        assistantName: assistantName,
        type: type,
      );
    } catch (e) {
      throw AIException(
        '获取用户提示词失败',
        code: 'GET_USER_PROMPTS_ERROR',
        details: e,
      );
    }
  }

  Future<void> updatePrompt(
    AIPrompt prompt, {
    required String userId,
  }) async {
    try {
      // 验证权限
      if (!_canModifyPrompt(prompt, userId)) {
        throw AIException(
          '无权修改此提示词',
          code: 'PROMPT_MODIFY_DENIED',
        );
      }

      // 验证内容
      final validationResult = await _validator.validate(
        prompt.content,
        'prompt_content',
        userId: userId,
      );
      if (!validationResult.isValid) {
        throw AIException(
          '提示词内容无效',
          code: 'INVALID_PROMPT_CONTENT',
          details: validationResult.errors,
        );
      }

      // 更新提示词
      await _savePrompt(prompt.copyWith(
        content: validationResult.sanitizedData,
      ));
      
      // 更新缓存
      _updatePromptCache(prompt);
    } catch (e) {
      throw AIException(
        '更新提示词失败',
        code: 'UPDATE_PROMPT_ERROR',
        details: e,
      );
    }
  }

  Future<void> deletePrompt(
    String promptId, {
    required String userId,
  }) async {
    try {
      final prompt = await getPrompt(promptId, userId: userId);
      
      // 验证权限
      if (!_canModifyPrompt(prompt, userId)) {
        throw AIException(
          '无权删除此提示词',
          code: 'PROMPT_DELETE_DENIED',
        );
      }

      // 删除提示词
      await _storageService.deletePrompt(promptId);
      
      // 从缓存移除
      _removeFromCache(promptId, userId);
    } catch (e) {
      throw AIException(
        '删除提示词失败',
        code: 'DELETE_PROMPT_ERROR',
        details: e,
      );
    }
  }

  bool _canCreatePrompt(String userId) {
    final plan = _subscriptionService.currentPlan;
    final config = _promptConfig[plan]!;
    final maxPrompts = config['max_custom_prompts'] as int;
    
    if (maxPrompts == -1) return true;
    
    final currentCount = _promptCache[userId]?.length ?? 0;
    return currentCount < maxPrompts;
  }

  bool _canAccessPrompt(AIPrompt prompt, String userId) {
    return prompt.userId == userId || prompt.type == PromptType.public;
  }

  bool _canModifyPrompt(AIPrompt prompt, String userId) {
    return prompt.userId == userId;
  }

  AIPrompt? _getFromCache(String promptId, String userId) {
    return _promptCache[userId]?[promptId];
  }

  void _updatePromptCache(AIPrompt prompt) {
    _promptCache
      .putIfAbsent(prompt.userId, () => {})
      [prompt.id] = prompt;
  }

  void _removeFromCache(String promptId, String userId) {
    _promptCache[userId]?.remove(promptId);
  }

  Future<void> _savePrompt(AIPrompt prompt) async {
    await _storageService.savePrompt(prompt);
  }
} 