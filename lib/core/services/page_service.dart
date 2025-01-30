import 'package:get/get.dart';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';

class PageService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();

  final pageStates = <String, Map<String, dynamic>>{}.obs;
  final pageHistory = <Map<String, dynamic>>[].obs;
  final currentPage = Rx<String?>(null);

  @override
  void onInit() {
    super.onInit();
    _initPageService();
  }

  Future<void> _initPageService() async {
    try {
      await _loadPageStates();
      await _loadPageHistory();
    } catch (e) {
      await _loggingService.log('error', 'Failed to initialize page service', data: {'error': e.toString()});
    }
  }

  // 保存页面状态
  Future<void> savePageState(String pageId, Map<String, dynamic> state) async {
    try {
      pageStates[pageId] = {
        ...state,
        'updated_at': DateTime.now().toIso8601String(),
      };
      await _savePageStates();
      await _recordPageAction(pageId, 'save_state', state);
    } catch (e) {
      await _loggingService.log('error', 'Failed to save page state', data: {'page_id': pageId, 'error': e.toString()});
      rethrow;
    }
  }

  // 恢复页面状态
  Future<Map<String, dynamic>?> restorePageState(String pageId) async {
    try {
      final state = pageStates[pageId];
      if (state != null) {
        await _recordPageAction(pageId, 'restore_state', state);
      }
      return state;
    } catch (e) {
      await _loggingService.log('error', 'Failed to restore page state', data: {'page_id': pageId, 'error': e.toString()});
      return null;
    }
  }

  // 清除页面状态
  Future<void> clearPageState(String pageId) async {
    try {
      pageStates.remove(pageId);
      await _savePageStates();
      await _recordPageAction(pageId, 'clear_state', null);
    } catch (e) {
      await _loggingService.log('error', 'Failed to clear page state', data: {'page_id': pageId, 'error': e.toString()});
      rethrow;
    }
  }

  // 记录页面访问
  Future<void> recordPageView(String pageId, Map<String, dynamic>? params) async {
    try {
      currentPage.value = pageId;
      await _recordPageAction(pageId, 'view', params);
    } catch (e) {
      await _loggingService.log('error', 'Failed to record page view', data: {'page_id': pageId, 'error': e.toString()});
      rethrow;
    }
  }

  // 记录页面事件
  Future<void> recordPageEvent(
    String pageId,
    String eventName,
    Map<String, dynamic>? data,
  ) async {
    try {
      await _recordPageAction(pageId, eventName, data);
    } catch (e) {
      await _loggingService.log('error', 'Failed to record page event', data: {'page_id': pageId, 'event': eventName, 'error': e.toString()});
      rethrow;
    }
  }

  // 获取页面访问历史
  Future<List<Map<String, dynamic>>> getPageHistory({
    String? pageId,
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    try {
      var history = pageHistory.toList();

      if (pageId != null) {
        history = history.where((record) => record['page_id'] == pageId).toList();
      }

      if (startDate != null || endDate != null) {
        history = history.where((record) {
          final timestamp = DateTime.parse(record['timestamp']);
          if (startDate != null && timestamp.isBefore(startDate)) return false;
          if (endDate != null && timestamp.isAfter(endDate)) return false;
          return true;
        }).toList();
      }

      return history;
    } catch (e) {
      await _loggingService.log('error', 'Failed to get page history', data: {'error': e.toString()});
      return [];
    }
  }

  Future<void> _loadPageStates() async {
    try {
      final states = await _storageService.getLocal('page_states');
      if (states != null) {
        pageStates.value = Map<String, Map<String, dynamic>>.from(states);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _savePageStates() async {
    try {
      await _storageService.saveLocal('page_states', pageStates.value);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _loadPageHistory() async {
    try {
      final history = await _storageService.getLocal('page_history');
      if (history != null) {
        pageHistory.value = List<Map<String, dynamic>>.from(history);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _savePageHistory() async {
    try {
      await _storageService.saveLocal('page_history', pageHistory);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _recordPageAction(
    String pageId,
    String action,
    dynamic data,
  ) async {
    try {
      final record = {
        'page_id': pageId,
        'action': action,
        'data': data,
        'timestamp': DateTime.now().toIso8601String(),
      };

      pageHistory.insert(0, record);
      
      // 只保留最近1000条记录
      if (pageHistory.length > 1000) {
        pageHistory.removeRange(1000, pageHistory.length);
      }
      
      await _savePageHistory();
    } catch (e) {
      rethrow;
    }
  }
} 