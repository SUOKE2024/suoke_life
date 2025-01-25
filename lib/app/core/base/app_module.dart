/// Application root module that manages all other modules
class AppModule extends BaseModule {
  @override
  String get name => 'app';

  @override
  String get version => '1.0.0';

  @override
  Future<void> onInitialize() async {
    try {
      // Register core modules in initialization order
      _registerCoreModules();

      // Register feature modules
      _registerFeatureModules();

      // Initialize all modules
      await ModuleDependencyManager.instance.initializeModules();

      LoggerService.info('Application modules initialized');
    } catch (e) {
      LoggerService.error('Failed to initialize application modules', error: e);
      rethrow;
    }
  }

  void _registerCoreModules() {
    // Core infrastructure modules
    ModuleDependencyManager.instance.registerModule(CoreModule());
    ModuleDependencyManager.instance.registerModule(NetworkModule());
    ModuleDependencyManager.instance.registerModule(StorageModule());
    
    // Core service modules
    ModuleDependencyManager.instance.registerModule(LoggingModule());
    ModuleDependencyManager.instance.registerModule(AnalyticsModule());
    ModuleDependencyManager.instance.registerModule(SecurityModule());
  }

  void _registerFeatureModules() {
    // Feature modules
    ModuleDependencyManager.instance.registerModule(ChatModule());
    ModuleDependencyManager.instance.registerModule(AiModule());
    ModuleDependencyManager.instance.registerModule(GamesModule());
  }

  @override
  Future<void> onDispose() async {
    await ModuleDependencyManager.instance.dispose();
  }

  @override
  Map<Type, BaseService> services() => {
    AppConfigManager: AppConfigManager.instance,
    ErrorHandler: ErrorHandler.instance,
  };
}

/// Initialize the application
Future<void> initializeApp() async {
  try {
    // Set up error handling
    ErrorHandler.initialize();

    // Initialize root module
    final appModule = AppModule();
    await appModule.onInitialize();

    LoggerService.info('Application initialized successfully');
  } catch (e) {
    LoggerService.error('Failed to initialize application', error: e);
    rethrow;
  }
} 