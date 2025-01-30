/// 模块依赖管理器
class ModuleDependencyManager {
  static final instance = ModuleDependencyManager._();
  ModuleDependencyManager._();

  final Map<Type, BaseModule> _modules = {};
  final Map<Type, List<Type>> _dependencies = {};
  bool _initialized = false;

  /// 注册模块
  void registerModule<T extends BaseModule>(T module) {
    if (_modules.containsKey(T)) {
      throw Exception('Module ${T.toString()} already registered');
    }
    _modules[T] = module;
    _dependencies[T] = module.dependencies;
  }

  /// 初始化所有模块
  Future<void> initializeModules() async {
    if (_initialized) return;

    try {
      // 检查循环依赖
      _checkCircularDependencies();

      // 按依赖顺序初始化模块
      final sortedModules = _sortModulesByDependencies();
      for (final moduleType in sortedModules) {
        final module = _modules[moduleType]!;
        await module.initialize();
      }

      _initialized = true;
      LoggerService.info('All modules initialized');
    } catch (e) {
      LoggerService.error('Failed to initialize modules', error: e);
      rethrow;
    }
  }

  /// 获取模块实例
  T getModule<T extends BaseModule>() {
    final module = _modules[T];
    if (module == null) {
      throw Exception('Module ${T.toString()} not registered');
    }
    return module as T;
  }

  /// 检查是否存在循环依赖
  void _checkCircularDependencies() {
    final visited = <Type>{};
    final recursionStack = <Type>{};

    void dfs(Type moduleType) {
      visited.add(moduleType);
      recursionStack.add(moduleType);

      for (final dependency in _dependencies[moduleType] ?? []) {
        if (!visited.contains(dependency)) {
          dfs(dependency);
        } else if (recursionStack.contains(dependency)) {
          throw Exception('Circular dependency detected: $moduleType -> $dependency');
        }
      }

      recursionStack.remove(moduleType);
    }

    for (final moduleType in _modules.keys) {
      if (!visited.contains(moduleType)) {
        dfs(moduleType);
      }
    }
  }

  /// 按依赖顺序排序模块
  List<Type> _sortModulesByDependencies() {
    final sorted = <Type>[];
    final visited = <Type>{};

    void visit(Type moduleType) {
      if (visited.contains(moduleType)) return;
      visited.add(moduleType);

      for (final dependency in _dependencies[moduleType] ?? []) {
        visit(dependency);
      }

      sorted.add(moduleType);
    }

    for (final moduleType in _modules.keys) {
      visit(moduleType);
    }

    return sorted;
  }

  /// 释放所有模块资源
  Future<void> dispose() async {
    if (!_initialized) return;

    try {
      // 按依赖顺序的反序释放模块
      final sortedModules = _sortModulesByDependencies().reversed;
      for (final moduleType in sortedModules) {
        final module = _modules[moduleType]!;
        await module.dispose();
      }

      _modules.clear();
      _dependencies.clear();
      _initialized = false;
      LoggerService.info('All modules disposed');
    } catch (e) {
      LoggerService.error('Failed to dispose modules', error: e);
      rethrow;
    }
  }
} 