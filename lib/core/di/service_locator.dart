import 'package:get_it/get_it.dart';
import 'registrars/core_module_registrar.dart';
import 'registrars/network_module_registrar.dart';
import 'registrars/realtime_module_registrar.dart';
import 'module_registrar.dart';

/// 依赖注入管理器
class ServiceLocator {
  static final GetIt _instance = GetIt.instance;
  
  static final List<ModuleRegistrar> _registrars = [
    CoreModuleRegistrar(),
    NetworkModuleRegistrar(),
    RealtimeModuleRegistrar(),
  ];

  /// 初始化所有服务
  static Future<void> init() async {
    try {
      // 同步注册
      for (final registrar in _registrars) {
        try {
          print('正在初始化${registrar.moduleName}...');
          await registrar.register(_instance);
          print('${registrar.moduleName}同步注册完成');
        } catch (e) {
          print('${registrar.moduleName}同步注册失败: $e');
          rethrow;
        }
      }
      
      // 异步注册
      try {
        print('开始异步服务注册...');
        await Future.wait(
          _registrars.map((registrar) => registrar.registerAsync(_instance)),
        );
        print('异步服务注册完成');
      } catch (e) {
        print('异步服务注册失败: $e');
        rethrow;
      }
      
      // 模块就绪回调
      for (final registrar in _registrars) {
        try {
          print('正在初始化${registrar.moduleName}的就绪回调...');
          await registrar.onModuleReady(_instance);
          print('${registrar.moduleName}就绪回调完成');
        } catch (e) {
          print('${registrar.moduleName}就绪回调失败: $e');
          rethrow;
        }
      }
      
      print('所有服务初始化完成');
    } catch (e, stackTrace) {
      print('服务初始化过程中发生错误: $e');
      print('错误堆栈: $stackTrace');
      await reset();  // 发生错误时重置所有服务
      rethrow;
    }
  }

  /// 获取服务实例
  static T get<T extends Object>() => _instance<T>();

  /// 重置所有服务（用于测试）
  static Future<void> reset() async {
    try {
      print('开始重置所有服务...');
      // 调用所有模块的销毁回调
      for (final registrar in _registrars.reversed) {  // 反向顺序销毁
        try {
          print('正在清理${registrar.moduleName}...');
          await registrar.onModuleDispose(_instance);
          print('${registrar.moduleName}清理完成');
        } catch (e) {
          print('${registrar.moduleName}清理失败: $e');
          // 继续清理其他模块
        }
      }
      
      // 重置 GetIt 实例
      await _instance.reset();
      print('所有服务重置完成');
    } catch (e, stackTrace) {
      print('服务重置过程中发生错误: $e');
      print('错误堆栈: $stackTrace');
      rethrow;
    }
  }

  /// 异步初始化服务（如果需要）
  static Future<void> initAsync<T extends Object>({
    required Future<T> Function() factory,
    String? instanceName,
    bool? signalsReady,
  }) async {
    try {
      print('正在异步初始化服务: ${T.toString()}...');
      await _instance.registerSingletonAsync(
        factory,
        instanceName: instanceName,
        signalsReady: signalsReady,
      );
      print('服务 ${T.toString()} 异步初始化完成');
    } catch (e) {
      print('服务 ${T.toString()} 异步初始化失败: $e');
      rethrow;
    }
  }
  
  /// 检查服务是否已注册
  static bool isRegistered<T extends Object>({String? instanceName}) {
    return _instance.isRegistered<T>(instanceName: instanceName);
  }
  
  /// 等待服务就绪
  static Future<void> waitForService<T extends Object>({String? instanceName}) {
    return _instance.isReady<T>(instanceName: instanceName);
  }
} 