import 'package:get/get.dart';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';

class RouteService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();

  final routeHistory = <Map<String, dynamic>>[].obs;
  final currentRoute = Rx<String?>(null);
  final previousRoute = Rx<String?>(null);

  @override
  void onInit() {
    super.onInit();
    _initRouteService();
  }

  Future<void> _initRouteService() async {
    try {
      await _loadRouteHistory();
      _setupRouteObserver();
    } catch (e) {
      await _loggingService.log('error', 'Failed to initialize route service', data: {'error': e.toString()});
    }
  }

  // 导航到指定路由
  Future<T?>? navigateTo<T>(
    String route, {
    dynamic arguments,
    bool preventDuplicates = true,
    Map<String, String>? parameters,
  }) async {
    try {
      previousRoute.value = currentRoute.value;
      currentRoute.value = route;

      await _recordRouteChange(route, arguments);
      
      return Get.toNamed<T>(
        route,
        arguments: arguments,
        preventDuplicates: preventDuplicates,
        parameters: parameters,
      );
    } catch (e) {
      await _loggingService.log('error', 'Failed to navigate', data: {'route': route, 'error': e.toString()});
      return null;
    }
  }

  // 返回上一页
  void goBack<T>({T? result}) {
    try {
      if (Get.currentRoute != '/') {
        Get.back<T>(result: result);
        
        currentRoute.value = previousRoute.value;
        previousRoute.value = null;
      }
    } catch (e) {
      _loggingService.log('error', 'Failed to go back', data: {'error': e.toString()});
    }
  }

  // 返回到指定路由
  void backTo(String route) {
    try {
      Get.until((r) => r.settings.name == route);
      
      currentRoute.value = route;
      previousRoute.value = null;
    } catch (e) {
      _loggingService.log('error', 'Failed to back to route', data: {'route': route, 'error': e.toString()});
    }
  }

  // 替换当前路由
  Future<T?>? replaceTo<T>(
    String route, {
    dynamic arguments,
    Map<String, String>? parameters,
  }) async {
    try {
      await _recordRouteChange(route, arguments);
      
      return Get.offNamed<T>(
        route,
        arguments: arguments,
        parameters: parameters,
      );
    } catch (e) {
      await _loggingService.log('error', 'Failed to replace route', data: {'route': route, 'error': e.toString()});
      return null;
    }
  }

  // 清除所有路由并导航
  Future<T?>? clearAndNavigateTo<T>(
    String route, {
    dynamic arguments,
    Map<String, String>? parameters,
  }) async {
    try {
      await _recordRouteChange(route, arguments);
      
      return Get.offAllNamed<T>(
        route,
        arguments: arguments,
        parameters: parameters,
      );
    } catch (e) {
      await _loggingService.log('error', 'Failed to clear and navigate', data: {'route': route, 'error': e.toString()});
      return null;
    }
  }

  void _setupRouteObserver() {
    Get.routing.observer?.onUnknownRoute = (settings) {
      _loggingService.log(
        'warning',
        'Unknown route',
        data: {'route': settings.name},
      );
      return null;
    };
  }

  Future<void> _recordRouteChange(String route, dynamic arguments) async {
    try {
      final record = {
        'route': route,
        'arguments': arguments,
        'timestamp': DateTime.now().toIso8601String(),
      };

      routeHistory.insert(0, record);
      
      // 只保留最近100条记录
      if (routeHistory.length > 100) {
        routeHistory.removeRange(100, routeHistory.length);
      }
      
      await _saveRouteHistory();
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _loadRouteHistory() async {
    try {
      final history = await _storageService.getLocal('route_history');
      if (history != null) {
        routeHistory.value = List<Map<String, dynamic>>.from(history);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveRouteHistory() async {
    try {
      await _storageService.saveLocal('route_history', routeHistory);
    } catch (e) {
      rethrow;
    }
  }
} 