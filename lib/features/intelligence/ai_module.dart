/// AI功能模块
class AiModule extends FeatureModule {
  @override
  String get name => 'ai';

  @override
  String get version => '1.0.0';

  @override
  List<String> get dependencies => [
    'storage',   // 依赖存储模块
    'network',   // 依赖网络模块
    'chat',      // 依赖聊天模块
  ];

  @override
  ModuleConfig? get config => _config;
  AiModuleConfig? _config;

  @override
  List<GetPage> get routes => [
    GetPage(
      name: Routes.AI_HOME,
      page: () => const AiHomePage(),
      binding: AiHomeBinding(),
    ),
    GetPage(
      name: Routes.AI_CHAT,
      page: () => const AiChatPage(),
      binding: AiChatBinding(),
      middlewares: [AiQuotaMiddleware()],
    ),
    GetPage(
      name: Routes.AI_IMAGE,
      page: () => const AiImagePage(),
      binding: AiImageBinding(),
      middlewares: [AiQuotaMiddleware()],
    ),
  ];

  @override
  List<GetMiddleware> get middleware => [
    AiAuthMiddleware(),    // AI功能鉴权
    AiQuotaMiddleware(),   // AI配额检查
  ];

  @override
  Map<Type, BaseService> services() => {
    AiService: AiService.instance,
    AiChatService: AiChatService.instance,
    AiImageService: AiImageService.instance,
  };

  @override
  Future<void> onInitialize() async {
    try {
      // 加载配置
      _config = await _loadConfig();

      // 初始化基类
      await super.onInitialize();

      // 初始化AI服务
      await _initializeAiServices();

      LoggerService.info('AI module initialized');
    } catch (e) {
      LoggerService.error('Failed to initialize AI module', error: e);
      rethrow;
    }
  }

  /// 加载模块配置
  Future<AiModuleConfig> _loadConfig() async {
    try {
      // 尝试从配置管理器加载
      final config = await getConfig<AiModuleConfig>();
      if (config != null) {
        return config;
      }

      // 使用默认配置
      return const AiModuleConfig(
        modelVersion: 'gpt-3.5-turbo',
        maxTokens: 2000,
        temperature: 0.7,
        imageSize: '512x512',
        defaultQuota: 100,
      );
    } catch (e) {
      LoggerService.error('Failed to load AI config', error: e);
      rethrow;
    }
  }

  /// 初始化AI服务
  Future<void> _initializeAiServices() async {
    try {
      // 获取依赖服务
      final storage = ServiceRegistry.instance.get<StorageService>();
      final network = ServiceRegistry.instance.get<NetworkService>();
      final chatService = ServiceRegistry.instance.get<ChatService>();

      // 初始化AI聊天服务
      final aiChatService = AiChatService.instance;
      await aiChatService.initialize(
        storage: storage,
        network: network,
        chatService: chatService,
        config: _config!,
      );

      // 初始化AI图像服务
      final aiImageService = AiImageService.instance;
      await aiImageService.initialize(
        storage: storage,
        network: network,
        config: _config!,
      );

      // 初始化AI核心服务
      final aiService = AiService.instance;
      await aiService.initialize(
        chatService: aiChatService,
        imageService: aiImageService,
        config: _config!,
      );
    } catch (e) {
      LoggerService.error('Failed to initialize AI services', error: e);
      rethrow;
    }
  }

  @override
  Future<void> onDispose() async {
    try {
      // 销毁服务
      await super.onDispose();
      
      // 清理配置
      _config = null;

      LoggerService.info('AI module disposed');
    } catch (e) {
      LoggerService.error('Failed to dispose AI module', error: e);
      rethrow;
    }
  }
} 