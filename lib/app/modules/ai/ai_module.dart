class AIModule extends AppModule {
  AIModule() : super(
    name: 'ai',
    version: '1.0.0',
    dependencies: ['core', 'network'],
  );

  @override
  Future<void> initialize() async {
    final config = AppConfigManager.instance.getModuleConfig(name);
    if (config != null) {
      await _initializeAIServices(config);
    }
  }

  Future<void> _initializeAIServices(ModuleConfig config) async {
    final aiService = AIService(
      endpoint: config.settings['endpoint'] as String,
      modelVersion: config.settings['modelVersion'] as String,
    );
    await aiService.initialize();
  }

  @override
  Map<Type, BaseService> services() => {
    AIService: AIService(),
    IntentRecognitionService: IntentRecognitionService(),
    LaokeService: LaokeService(),
    XiaoiService: XiaoiService(),
  };

  @override
  List<GetPage> routes() => [
    GetPage(
      name: Routes.AI_CHAT,
      page: () => const AIChatPage(),
      binding: AIChatBinding(),
    ),
    GetPage(
      name: Routes.AI_SETTINGS,
      page: () => const AISettingsPage(),
      binding: AISettingsBinding(),
    ),
  ];

  @override
  List<Binding> bindings() => [
    AIChatBinding(),
    AISettingsBinding(),
  ];
} 