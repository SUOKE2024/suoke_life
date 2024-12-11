class GamesModule extends AppModule {
  GamesModule() : super(
    name: 'games',
    version: '1.0.0',
    dependencies: ['core', 'network'],
  );

  @override
  Future<void> initialize() async {
    final config = AppConfigManager.instance.getModuleConfig(name);
    await _initializeGameServices(config);
  }

  Future<void> _initializeGameServices(ModuleConfig? config) async {
    final gameService = GameService(
      maxPlayers: config?.settings['maxPlayers'] as int? ?? 10,
      enableAR: config?.settings['enableAR'] as bool? ?? false,
    );
    await gameService.initialize();
  }

  @override
  Map<Type, BaseService> services() => {
    GameService: GameService(),
    ARService: ARService(),
    LeaderboardService: LeaderboardService(),
  };

  @override
  List<GetPage> routes() => [
    GetPage(
      name: Routes.GAMES_HOME,
      page: () => const GamesHomePage(),
      binding: GamesBinding(),
    ),
    GetPage(
      name: Routes.TREASURE_QUEST,
      page: () => const TreasureQuestPage(),
      binding: TreasureQuestBinding(),
    ),
    GetPage(
      name: Routes.LEADERBOARD,
      page: () => const LeaderboardPage(),
      binding: LeaderboardBinding(),
    ),
  ];

  @override
  List<Binding> bindings() => [
    GamesBinding(),
    TreasureQuestBinding(),
    LeaderboardBinding(),
  ];
} 