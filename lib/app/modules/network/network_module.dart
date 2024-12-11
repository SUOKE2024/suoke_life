class NetworkModule extends AppModule {
  NetworkModule() : super(
    name: 'network',
    version: '1.0.0',
    dependencies: ['core'],
  );

  @override
  Future<void> initialize() async {
    final config = AppConfigManager.instance.getModuleConfig(name);
    await _initializeNetworkServices();
  }

  Future<void> _initializeNetworkServices() async {
    final networkService = NetworkService(
      baseUrl: EnvConfig.instance.apiUrl,
      timeout: const Duration(seconds: 30),
      interceptors: [
        AuthInterceptor(),
        LoggingInterceptor(),
        ErrorInterceptor(),
      ],
    );
    await networkService.initialize();
  }

  @override
  Map<Type, BaseService> services() => {
    NetworkService: NetworkService(),
    WebSocketService: WebSocketService(),
    ConnectionMonitor: ConnectionMonitor(),
  };

  @override
  List<GetPage> routes() => [];

  @override
  List<Binding> bindings() => [
    NetworkBinding(),
  ];
} 