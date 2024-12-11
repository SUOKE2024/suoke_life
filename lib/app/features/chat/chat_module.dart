/// 聊天模块
class ChatModule extends BaseModule {
  @override
  String get name => 'chat';

  @override
  List<String> get dependencies => ['auth', 'storage'];

  @override
  ModuleConfig get config => const ModuleConfig(
    lazyLoad: true,
    priority: 1,
  );

  @override
  Future<void> onInit() async {
    // 初始化聊天服务
    final chatService = Get.put(ChatService());
    await chatService.onInit();
    
    // 初始化消息服务
    final messageService = Get.put(MessageService());
    await messageService.onInit();
    
    LoggerService.info('Chat module initialized');
  }

  @override
  Map<String, BaseService> getServices() => {
    'chat': Get.find<ChatService>(),
    'message': Get.find<MessageService>(),
  };

  @override
  List<GetPage> getRoutes() => [
    GetPage(
      name: Routes.CHAT_LIST,
      page: () => const ChatListPage(),
      binding: ChatBinding(),
      middlewares: [AuthMiddleware()],
    ),
    GetPage(
      name: Routes.CHAT_DETAIL,
      page: () => const ChatDetailPage(),
      binding: ChatDetailBinding(),
      middlewares: [AuthMiddleware()],
    ),
  ];

  @override
  List<MiddlewareBase> getMiddleware() => [
    ChatMiddleware(),
  ];

  @override
  List<Bind> getBindings() => [
    Bind.singleton((i) => ChatService()),
    Bind.singleton((i) => MessageService()),
    Bind.factory((i) => ChatController()),
  ];
} 