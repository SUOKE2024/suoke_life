import 'package:get_it/get_it.dart';

/// 模块注册器接口
abstract class ModuleRegistrar {
  /// 获取模块名称
  String get moduleName;
  
  /// 获取模块依赖
  List<Type> get dependencies => [];

  /// 注册模块的所有依赖
  Future<void> register(GetIt getIt);
  
  /// 注册模块的异步依赖
  Future<void> registerAsync(GetIt getIt) async {}
  
  /// 模块初始化后的回调
  Future<void> onModuleReady(GetIt getIt) async {}
  
  /// 模块销毁时的回调
  Future<void> onModuleDispose(GetIt getIt) async {}
  
  /// 验证模块依赖
  Future<void> validateDependencies(GetIt getIt) async {
    for (final dependency in dependencies) {
      if (!getIt.isRegistered<dynamic>(instanceName: dependency.toString())) {
        throw MissingDependencyError(
          moduleName: moduleName,
          dependencyType: dependency,
        );
      }
      
      try {
        // 检查异步依赖是否就绪
        if (getIt.isRegisteredAsync<dynamic>(instanceName: dependency.toString())) {
          await getIt.isReady<dynamic>(instanceName: dependency.toString());
        }
      } catch (e) {
        throw DependencyNotReadyError(
          moduleName: moduleName,
          dependencyType: dependency,
          error: e,
        );
      }
    }
  }
}

/// 缺失依赖错误
class MissingDependencyError extends Error {
  final String moduleName;
  final Type dependencyType;

  MissingDependencyError({
    required this.moduleName,
    required this.dependencyType,
  });

  @override
  String toString() => 
    '模块 "$moduleName" 缺少必要的依赖: ${dependencyType.toString()}';
}

/// 依赖未就绪错误
class DependencyNotReadyError extends Error {
  final String moduleName;
  final Type dependencyType;
  final Object error;

  DependencyNotReadyError({
    required this.moduleName,
    required this.dependencyType,
    required this.error,
  });

  @override
  String toString() => 
    '模块 "$moduleName" 的依赖 ${dependencyType.toString()} 未就绪: $error';
} 