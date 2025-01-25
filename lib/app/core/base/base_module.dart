/// 基础模块抽象类
abstract class BaseModule {
  /// 模块名称
  String get name;
  
  /// 模块依赖
  List<String> get dependencies => const [];
  
  /// 模块配置
  ModuleConfig get config => const ModuleConfig();
  
  /// 初始化模块
  Future<void> onInit() async {}
  
  /// 销毁模块
  Future<void> onDispose() async {}
  
  /// 获取模块服务
  Map<String, BaseService> getServices() => {};
  
  /// 获取模块路由
  List<GetPage> getRoutes() => [];
  
  /// 获取模块中间件
  List<MiddlewareBase> getMiddleware() => [];
  
  /// 获取模块绑定
  List<Bind> getBindings() => [];
}

/// 模块配置
class ModuleConfig {
  /// 是否懒加载
  final bool lazyLoad;
  
  /// 是否启用
  final bool enabled;
  
  /// 优先级(越小越优先)
  final int priority;
  
  /// 超时时间
  final Duration timeout;

  const ModuleConfig({
    this.lazyLoad = false,
    this.enabled = true,
    this.priority = 0,
    this.timeout = const Duration(seconds: 10),
  });
}

/// 模块状态
enum ModuleState {
  /// 未初始化
  uninitialized,
  
  /// 初始化中
  initializing,
  
  /// 已初始化
  initialized,
  
  /// 初始化失败
  failed,
  
  /// 已禁用
  disabled,
}

/// 模块生命周期事件
abstract class ModuleEvent {
  final String moduleName;
  final DateTime timestamp;

  ModuleEvent(this.moduleName) : timestamp = DateTime.now();
}

class ModuleInitializedEvent extends ModuleEvent {
  ModuleInitializedEvent(super.moduleName);
}

class ModuleFailedEvent extends ModuleEvent {
  final dynamic error;
  ModuleFailedEvent(super.moduleName, this.error);
}

class ModuleDisabledEvent extends ModuleEvent {
  ModuleDisabledEvent(super.moduleName);
}

abstract class FeatureModule extends BaseModule {
  String get featureKey;
  BaseService? get service;
  BaseController? get controller;
} 