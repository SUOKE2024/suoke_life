class AIModule extends GetxService {
  @override
  void onInit() {
    super.onInit();
    _registerDependencies();
  }

  void _registerDependencies() {
    // 注册基础服务
    Get.lazyPut<AIService>(
      () => AIService(),
      fenix: true,
    );

    // 注册助手服务
    Get.lazyPut<AIAssistantService>(
      () => AIAssistantService(
        aiService: Get.find<AIService>(),
      ),
      fenix: true,
    );

    // 注册服务管理器
    Get.lazyPut<AIServiceManager>(
      () => AIServiceManager(
        subscriptionService: Get.find<SubscriptionService>(),
        assistantService: Get.find<AIAssistantService>(),
      ),
      fenix: true,
    );

    // 新增服务注册
    Get.lazyPut<ModelManagerService>(
      () => ModelManagerService(subscriptionService: Get.find()),
      fenix: true,
    );
    
    Get.lazyPut<ChatHistoryService>(
      () => ChatHistoryService(
        storageService: Get.find(),
        subscriptionService: Get.find(),
      ),
      fenix: true,
    );
    
    Get.lazyPut<ContextManagerService>(
      () => ContextManagerService(subscriptionService: Get.find()),
      fenix: true,
    );
    
    Get.lazyPut<AnalysisService>(
      () => AnalysisService(
        aiService: Get.find(),
        subscriptionService: Get.find(),
        historyService: Get.find(),
      ),
      fenix: true,
    );

    // 添加会话管理服务
    Get.lazyPut<SessionManagerService>(
      () => SessionManagerService(
        contextManager: Get.find(),
        historyService: Get.find(),
        modelManager: Get.find(),
        subscriptionService: Get.find(),
      ),
      fenix: true,
    );

    // 添加事件追踪服务
    Get.lazyPut<EventTrackingService>(
      () => EventTrackingService(
        analysisService: Get.find(),
        subscriptionService: Get.find(),
        storageService: Get.find(),
      ),
      fenix: true,
    );

    // 添加反馈服务
    Get.lazyPut<FeedbackService>(
      () => FeedbackService(
        storageService: Get.find(),
        analysisService: Get.find(),
        eventTracking: Get.find(),
      ),
      fenix: true,
    );

    // 添加性能监控服务
    Get.lazyPut<PerformanceMonitorService>(
      () => PerformanceMonitorService(
        storageService: Get.find(),
        eventTracking: Get.find(),
        subscriptionService: Get.find(),
      ),
      fenix: true,
    );

    // 添加健康检查服务
    Get.lazyPut<HealthCheckService>(
      () => HealthCheckService(
        modelManager: Get.find(),
        performanceMonitor: Get.find(),
        eventTracking: Get.find(),
        subscriptionService: Get.find(),
      ),
      fenix: true,
    );

    // 添加降级服务
    Get.lazyPut<FallbackService>(
      () => FallbackService(
        modelManager: Get.find(),
        healthCheck: Get.find(),
        eventTracking: Get.find(),
        subscriptionService: Get.find(),
      ),
      fenix: true,
    );

    // 添加配额管理服务
    Get.lazyPut<QuotaManagerService>(
      () => QuotaManagerService(
        subscriptionService: Get.find(),
        storageService: Get.find(),
        eventTracking: Get.find(),
      ),
      fenix: true,
    );

    // 添加日志管理服务
    Get.lazyPut<LogManagerService>(
      () => LogManagerService(
        storageService: Get.find(),
        eventTracking: Get.find(),
        subscriptionService: Get.find(),
      ),
      fenix: true,
    );

    // 添加缓存管理服务
    Get.lazyPut<CacheManagerService>(
      () => CacheManagerService(
        storageService: Get.find(),
        subscriptionService: Get.find(),
      ),
      fenix: true,
    );

    // 添加安全管理服务
    Get.lazyPut<SecurityManagerService>(
      () => SecurityManagerService(
        subscriptionService: Get.find(),
        eventTracking: Get.find(),
        logManager: Get.find(),
      ),
      fenix: true,
    );

    // 添加同步服务
    Get.lazyPut<SyncManagerService>(
      () => SyncManagerService(
        storageService: Get.find(),
        securityManager: Get.find(),
        eventTracking: Get.find(),
      ),
      fenix: true,
    );

    // 添加任务调度服务
    Get.lazyPut<TaskSchedulerService>(
      () => TaskSchedulerService(
        eventTracking: Get.find(),
        logManager: Get.find(),
      ),
      fenix: true,
    );

    // 添加数据分析服务
    Get.lazyPut<DataAnalysisService>(
      () => DataAnalysisService(
        aiService: Get.find(),
        storageService: Get.find(),
        eventTracking: Get.find(),
        subscriptionService: Get.find(),
      ),
      fenix: true,
    );

    // 添加通知管理服务
    Get.lazyPut<NotificationManagerService>(
      () => NotificationManagerService(
        subscriptionService: Get.find(),
        eventTracking: Get.find(),
        logManager: Get.find(),
      ),
      fenix: true,
    );

    // 添加权限管理服务
    Get.lazyPut<PermissionManagerService>(
      () => PermissionManagerService(
        subscriptionService: Get.find(),
        securityManager: Get.find(),
        eventTracking: Get.find(),
        logManager: Get.find(),
      ),
      fenix: true,
    );

    // 添加配置管理服务
    Get.lazyPut<ConfigManagerService>(
      () => ConfigManagerService(
        storageService: Get.find(),
        securityManager: Get.find(),
        eventTracking: Get.find(),
        permissionManager: Get.find(),
      ),
      fenix: true,
    );

    // 添加数据验证服务
    Get.lazyPut<ValidationService>(
      () => ValidationService(
        aiService: Get.find(),
        securityManager: Get.find(),
        eventTracking: Get.find(),
        subscriptionService: Get.find(),
      ),
      fenix: true,
    );

    // 添加错误处理服务
    Get.lazyPut<ErrorHandlerService>(
      () => ErrorHandlerService(
        logManager: Get.find(),
        eventTracking: Get.find(),
        notificationManager: Get.find(),
        fallbackService: Get.find(),
      ),
      fenix: true,
    );

    // 添加提示词管理服务
    Get.lazyPut<PromptManagerService>(
      () => PromptManagerService(
        storageService: Get.find(),
        securityManager: Get.find(),
        validator: Get.find(),
        subscriptionService: Get.find(),
      ),
      fenix: true,
    );

    // 添加知识库管理服务
    Get.lazyPut<KnowledgeManagerService>(
      () => KnowledgeManagerService(
        storageService: Get.find(),
        securityManager: Get.find(),
        validator: Get.find(),
        subscriptionService: Get.find(),
        eventTracking: Get.find(),
      ),
      fenix: true,
    );

    // 添加数据存储服务
    Get.lazyPut<StorageService>(
      () => StorageService(
        securityManager: Get.find(),
        cacheManager: Get.find(),
        syncManager: Get.find(),
      ),
      fenix: true,
    );

    // 添加订阅管理服务
    Get.lazyPut<SubscriptionService>(
      () => SubscriptionService(
        storageService: Get.find(),
        eventTracking: Get.find(),
        securityManager: Get.find(),
      ),
      fenix: true,
    );
  }

  @override
  void onReady() {
    super.onReady();
    // 预热模型
    Get.find<ModelManagerService>().warmupModels();
  }
} 