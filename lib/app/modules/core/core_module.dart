class CoreModule extends AppModule {
  CoreModule() : super(
    name: 'core',
    version: '1.0.0',
  );

  @override
  Future<void> initialize() async {
    await _initializeStorage();
    await _initializeAuth();
    await _initializeLogger();
  }

  Future<void> _initializeStorage() async {
    final storageService = StorageService();
    await storageService.initialize();
  }

  Future<void> _initializeAuth() async {
    final authService = AuthService(
      storage: ServiceManager.instance.getService<StorageService>()!,
    );
    await authService.initialize();
  }

  Future<void> _initializeLogger() async {
    final loggerService = LoggerService(
      enableConsoleOutput: EnvConfig.instance.enableLogging,
    );
    await loggerService.initialize();
  }

  @override
  Map<Type, BaseService> services() => {
    StorageService: StorageService(),
    AuthService: AuthService(),
    LoggerService: LoggerService(),
    SecurityService: SecurityService(),
  };

  @override
  List<GetPage> routes() => [
    GetPage(
      name: Routes.LOGIN,
      page: () => const LoginPage(),
      binding: LoginBinding(),
    ),
    GetPage(
      name: Routes.REGISTER,
      page: () => const RegisterPage(),
      binding: RegisterBinding(),
    ),
  ];

  @override
  List<Binding> bindings() => [
    CoreBinding(),
    AuthBinding(),
  ];
} 