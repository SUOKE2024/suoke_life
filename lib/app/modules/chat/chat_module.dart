class ChatModule extends AppModule {
  ChatModule() : super(
    name: 'chat',
    version: '1.0.0',
    dependencies: ['core', 'network'],
  );

  @override
  Future<void> initialize() async {
    final config = AppConfigManager.instance.getModuleConfig(name);
    // 初始化模块配置
  }

  @override
  Map<Type, BaseService> services() => {
    ChatService: ChatService(),
    MessageService: MessageService(),
  };

  @override
  List<GetPage> routes() => [
    GetPage(
      name: Routes.CHAT_LIST,
      page: () => const ChatListPage(),
      binding: ChatBinding(),
    ),
    GetPage(
      name: Routes.CHAT_DETAIL,
      page: () => const ChatDetailPage(),
      binding: ChatDetailBinding(),
    ),
  ];

  @override
  List<Binding> bindings() => [
    ChatBinding(),
    ChatDetailBinding(),
  ];
} 