class ModuleRegistry {
  static final Map<String, BaseModule> _modules = {};
  
  static void registerModule(BaseModule module) {
    if (!_modules.containsKey(module.name)) {
      _modules[module.name] = module;
    }
  }

  static Future<void> initializeModules() async {
    for (final module in _modules.values) {
      await module.init();
    }
  }

  static List<GetPage> get pages {
    return _modules.values.expand((m) => m.pages).toList();
  }

  static List<Bindings> get bindings {
    return _modules.values.expand((m) => m.bindings).toList();
  }
} 