class ServiceContainer {
  static final _instance = ServiceContainer._();
  factory ServiceContainer() => _instance;
  ServiceContainer._();

  final _services = <Type, dynamic>{};
  final _factories = <Type, Function>{};

  T get<T>() {
    if (_services.containsKey(T)) {
      return _services[T] as T;
    }
    
    if (_factories.containsKey(T)) {
      final instance = _factories[T]!();
      _services[T] = instance;
      return instance as T;
    }
    
    throw ServiceNotFoundException('Service $T not registered');
  }

  void register<T>(T instance, {bool singleton = true}) {
    if (singleton) {
      _services[T] = instance;
    } else {
      _factories[T] = () => instance;
    }
  }

  void registerFactory<T>(T Function() factory) {
    _factories[T] = factory;
  }
} 