/// 聊天模块
class ChatModule extends BaseModule {
  static final instance = ChatModule._();
  ChatModule._();

  late final ChatService _chatService;
  late final ChatRepository _chatRepository;
  late final ChatController _chatController;

  @override
  List<Type> get dependencies => [
        StorageService,
        NetworkService,
        AuthService,
      ];

  @override
  Future<void> initialize() async {
    if (isInitialized) return;

    try {
      // 获取依赖服务
      final storageService = ServiceRegistry.instance.get<StorageService>();
      final networkService = ServiceRegistry.instance.get<NetworkService>();
      final authService = ServiceRegistry.instance.get<AuthService>();

      // 初始化仓库
      _chatRepository = ChatRepository(
        storageService: storageService,
        networkService: networkService,
      );

      // 初始化服务
      _chatService = ChatService(
        repository: _chatRepository,
        authService: authService,
      );

      // 初始化控制器
      _chatController = ChatController(
        service: _chatService,
      );

      isInitialized = true;
      LoggerService.info('Chat module initialized');
    } catch (e) {
      LoggerService.error('Failed to initialize chat module', error: e);
      rethrow;
    }
  }

  @override
  Future<void> dispose() async {
    if (!isInitialized) return;

    try {
      await _chatService.dispose();
      isInitialized = false;
      LoggerService.info('Chat module disposed');
    } catch (e) {
      LoggerService.error('Failed to dispose chat module', error: e);
      rethrow;
    }
  }

  // 公开服务和控制器
  ChatService get chatService => _chatService;
  ChatController get chatController => _chatController;
} 