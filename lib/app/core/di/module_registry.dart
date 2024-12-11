class ModuleRegistry {
  static final _modules = <String, BaseModule>{};
  
  static void registerModules() {
    // 核心模块
    _register([
      CoreModule(),
      NetworkModule(),
      StorageModule(),
    ]);
    
    // 功能模块
    _register([
      ChatModule(),
      AIModule(),
      GamesModule(),
    ]);
  }
  
  static void _register(List<BaseModule> modules) {
    for (final module in modules) {
      if (_modules.containsKey(module.name)) {
        throw ModuleAlreadyRegisteredException(module.name);
      }
      _modules[module.name] = module;
    }
  }
} 