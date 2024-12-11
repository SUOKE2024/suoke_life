class ServiceLifecycleManager {
  final _services = <Type, BaseService>{};
  
  Future<void> initializeServices() async {
    for (final service in _services.values) {
      if (!service.isInitialized) {
        await service.initialize();
      }
    }
  }
  
  Future<void> disposeServices() async {
    for (final service in _services.values) {
      await service.dispose();
    }
    _services.clear();
  }
} 