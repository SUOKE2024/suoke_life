import 'package:get/get.dart';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';
import 'middleware_service.dart';

class NavigationService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();
  final MiddlewareService _middlewareService = Get.find();

  final navigationStack = <String>[].obs;
  final navigationHistory = <Map<String, dynamic>>[].obs;
  final navigationState = <String, dynamic>{}.obs;

  @override
  void onInit() {
    super.onInit();
    _initNavigation();
  }

  Future<void> _initNavigation() async {
    try {
      await _loadNavigationHistory();
      await _loadNavigationState();
    } catch (e) {
      await _loggingService.log('error', 'Failed to initialize navigation', data: {'error': e.toString()});
    }
  }

  // 导航到页面
  Future<T?> navigateToPage<T>(
    String page, {
    dynamic arguments,
    Map<String, String>? parameters,
    bool preventDuplicates = true,
    List<String>? middleware,
  }) async {
    try {
      // 检查中间件
      if (middleware != null) {
        for (final m in middleware) {
          final allowed = await _middlewareService.runMiddleware(m, {
            'page': page,
            'arguments': arguments,
            'parameters': parameters,
          });
          if (!allowed) {
            await _loggingService.log('warning', 'Navigation blocked by middleware', data: {'middleware': m, 'page': page});
            return null;
          }
        }
      }

      // 更新导航栈
      if (preventDuplicates && navigationStack.contains(page)) {
        navigationStack.remove(page);
      }
      navigationStack.add(page);

      // 记录导航历史
      await _recordNavigation(page, arguments, parameters);

      // 执行导航
      return Get.toNamed<T>(
        page,
        arguments: arguments,
        parameters: parameters,
        preventDuplicates: preventDuplicates,
      );
    } catch (e) {
      await _loggingService.log('error', 'Failed to navigate to page', data: {'page': page, 'error': e.toString()});
      return null;
    }
  }

  // 返回上一页
  Future<void> goBack<T>({T? result}) async {
    try {
      if (navigationStack.isNotEmpty) {
        final currentPage = navigationStack.last;
        navigationStack.removeLast();
        
        await _recordNavigation(
          navigationStack.isEmpty ? '/' : navigationStack.last,
          null,
          null,
          previousPage: currentPage,
        );
        
        Get.back<T>(result: result);
      }
    } catch (e) {
      await _loggingService.log('error', 'Failed to go back', data: {'error': e.toString()});
    }
  }

  // 返回到指定页面
  Future<void> backToPage(String page) async {
    try {
      final index = navigationStack.indexOf(page);
      if (index != -1) {
        final removedPages = navigationStack.sublist(index + 1);
        navigationStack.removeRange(index + 1, navigationStack.length);
        
        await _recordNavigation(
          page,
          null,
          null,
          removedPages: removedPages,
        );
        
        Get.until((route) => route.settings.name == page);
      }
    } catch (e) {
      await _loggingService.log('error', 'Failed to back to page', data: {'page': page, 'error': e.toString()});
    }
  }

  // 保存导航状态
  Future<void> saveNavigationState(String key, dynamic value) async {
    try {
      navigationState[key] = value;
      await _saveNavigationState();
    } catch (e) {
      await _loggingService.log('error', 'Failed to save navigation state', data: {'key': key, 'error': e.toString()});
      rethrow;
    }
  }

  // 获取导航状态
  T? getNavigationState<T>(String key, {T? defaultValue}) {
    try {
      return navigationState[key] as T? ?? defaultValue;
    } catch (e) {
      _loggingService.log('error', 'Failed to get navigation state', data: {'key': key, 'error': e.toString()});
      return defaultValue;
    }
  }

  Future<void> _loadNavigationHistory() async {
    try {
      final history = await _storageService.getLocal('navigation_history');
      if (history != null) {
        navigationHistory.value = List<Map<String, dynamic>>.from(history);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveNavigationHistory() async {
    try {
      await _storageService.saveLocal('navigation_history', navigationHistory);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _loadNavigationState() async {
    try {
      final state = await _storageService.getLocal('navigation_state');
      if (state != null) {
        navigationState.value = Map<String, dynamic>.from(state);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveNavigationState() async {
    try {
      await _storageService.saveLocal('navigation_state', navigationState);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _recordNavigation(
    String page,
    dynamic arguments,
    Map<String, String>? parameters, {
    String? previousPage,
    List<String>? removedPages,
  }) async {
    try {
      final record = {
        'page': page,
        'arguments': arguments,
        'parameters': parameters,
        'previous_page': previousPage,
        'removed_pages': removedPages,
        'timestamp': DateTime.now().toIso8601String(),
      };

      navigationHistory.insert(0, record);
      
      // 只保留最近1000条记录
      if (navigationHistory.length > 1000) {
        navigationHistory.removeRange(1000, navigationHistory.length);
      }
      
      await _saveNavigationHistory();
    } catch (e) {
      rethrow;
    }
  }
} 