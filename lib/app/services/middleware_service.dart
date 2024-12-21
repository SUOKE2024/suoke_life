import 'package:get/get.dart';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';
import 'auth_service.dart';

class MiddlewareService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();
  final AuthService _authService = Get.find();

  final middlewareStack = <String, List<Function>>{}.obs;
  final middlewareHistory = <Map<String, dynamic>>[].obs;

  @override
  void onInit() {
    super.onInit();
    _initMiddleware();
  }

  Future<void> _initMiddleware() async {
    try {
      await _loadMiddlewareHistory();
      _registerDefaultMiddleware();
    } catch (e) {
      await _loggingService.log('error', 'Failed to initialize middleware', data: {'error': e.toString()});
    }
  }

  // 注册中间件
  void registerMiddleware(String name, Function middleware) {
    try {
      if (!middlewareStack.containsKey(name)) {
        middlewareStack[name] = [];
      }
      middlewareStack[name]!.add(middleware);
    } catch (e) {
      _loggingService.log('error', 'Failed to register middleware', data: {'name': name, 'error': e.toString()});
    }
  }

  // 移除中间件
  void removeMiddleware(String name) {
    try {
      middlewareStack.remove(name);
    } catch (e) {
      _loggingService.log('error', 'Failed to remove middleware', data: {'name': name, 'error': e.toString()});
    }
  }

  // 执行中间件
  Future<bool> runMiddleware(String name, dynamic data) async {
    try {
      final middlewares = middlewareStack[name];
      if (middlewares == null || middlewares.isEmpty) {
        return true;
      }

      for (final middleware in middlewares) {
        final result = await middleware(data);
        if (result == false) {
          await _recordMiddlewareExecution(name, false);
          return false;
        }
      }

      await _recordMiddlewareExecution(name, true);
      return true;
    } catch (e) {
      await _loggingService.log('error', 'Failed to run middleware', data: {'name': name, 'error': e.toString()});
      return false;
    }
  }

  void _registerDefaultMiddleware() {
    // 认证中间件
    registerMiddleware('auth', (data) async {
      return await _authService.isAuthenticated();
    });

    // 权限中间件
    registerMiddleware('permission', (data) async {
      if (data is! List<String>) return false;
      return await _checkPermissions(data);
    });

    // 角色中间件
    registerMiddleware('role', (data) async {
      if (data is! List<String>) return false;
      return await _checkRoles(data);
    });

    // 缓存中间件
    registerMiddleware('cache', (data) async {
      return await _checkCache(data);
    });

    // 限流中间件
    registerMiddleware('throttle', (data) async {
      return await _checkThrottle(data);
    });
  }

  Future<bool> _checkPermissions(List<String> permissions) async {
    try {
      final userPermissions = await _authService.getUserPermissions();
      return permissions.every((p) => userPermissions.contains(p));
    } catch (e) {
      return false;
    }
  }

  Future<bool> _checkRoles(List<String> roles) async {
    try {
      final userRoles = await _authService.getUserRoles();
      return roles.every((r) => userRoles.contains(r));
    } catch (e) {
      return false;
    }
  }

  Future<bool> _checkCache(dynamic data) async {
    try {
      if (data is! String) return false;
      final cached = await _storageService.getLocal(data);
      return cached != null;
    } catch (e) {
      return false;
    }
  }

  Future<bool> _checkThrottle(dynamic data) async {
    try {
      if (data is! Map<String, dynamic>) return false;
      
      final key = data['key'] as String?;
      final limit = data['limit'] as int?;
      final duration = data['duration'] as int?;
      
      if (key == null || limit == null || duration == null) {
        return false;
      }

      final throttleKey = 'throttle:$key';
      final records = await _getThrottleRecords(throttleKey);
      
      // 清理过期记录
      final now = DateTime.now();
      records.removeWhere((r) {
        final timestamp = DateTime.parse(r['timestamp']);
        return now.difference(timestamp).inSeconds > duration;
      });

      if (records.length >= limit) {
        return false;
      }

      records.add({
        'timestamp': now.toIso8601String(),
      });

      await _storageService.saveLocal(throttleKey, records);
      return true;
    } catch (e) {
      return false;
    }
  }

  Future<List<Map<String, dynamic>>> _getThrottleRecords(String key) async {
    try {
      final records = await _storageService.getLocal(key);
      return records != null ? List<Map<String, dynamic>>.from(records) : [];
    } catch (e) {
      return [];
    }
  }

  Future<void> _recordMiddlewareExecution(String name, bool success) async {
    try {
      final record = {
        'middleware': name,
        'success': success,
        'timestamp': DateTime.now().toIso8601String(),
      };

      middlewareHistory.insert(0, record);
      
      // 只保留��近100条记录
      if (middlewareHistory.length > 100) {
        middlewareHistory.removeRange(100, middlewareHistory.length);
      }
      
      await _saveMiddlewareHistory();
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _loadMiddlewareHistory() async {
    try {
      final history = await _storageService.getLocal('middleware_history');
      if (history != null) {
        middlewareHistory.value = List<Map<String, dynamic>>.from(history);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveMiddlewareHistory() async {
    try {
      await _storageService.saveLocal('middleware_history', middlewareHistory);
    } catch (e) {
      rethrow;
    }
  }
} 