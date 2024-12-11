class ServiceManager {
  static final instance = ServiceManager._();
  ServiceManager._();

  final _services = <Type, BaseService>{};
  final _moduleServices = <String, Map<Type, BaseService>>{};

  Future<void> registerModule(AppModule module) async {
    if (_moduleServices.containsKey(module.name)) {
      throw ModuleAlreadyRegisteredException(module.name);
    }

    final services = module.services();
    _moduleServices[module.name] = services;
    _services.addAll(services);

    await _initializeModuleServices(module.name);
  }

  Future<void> _initializeModuleServices(String moduleName) async {
    final services = _moduleServices[moduleName];
    if (services == null) return;

    for (final service in services.values) {
      if (!service.isInitialized) {
        await service.initialize();
      }
    }
  }

  T? getService<T extends BaseService>() {
    return _services[T] as T?;
  }
} 