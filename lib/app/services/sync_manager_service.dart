import 'package:get/get.dart';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';
import 'network_service.dart';

class SyncManagerService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();
  final NetworkService _networkService = Get.find();

  final isSyncing = false.obs;
  final syncProgress = 0.0.obs;
  final lastSyncTime = Rx<DateTime?>(null);

  // 同步数据
  Future<void> syncData() async {
    if (isSyncing.value || !_networkService.isConnected.value) return;

    try {
      isSyncing.value = true;
      syncProgress.value = 0;

      // 获取需要同步的数据
      final syncData = await _collectSyncData();
      syncProgress.value = 0.3;

      // 上传数据
      await _uploadData(syncData);
      syncProgress.value = 0.6;

      // 下载数据
      await _downloadData();
      syncProgress.value = 0.9;

      // 合并数据
      await _mergeData();
      syncProgress.value = 1.0;

      // 更新同步时间
      await _updateLastSyncTime();
    } catch (e) {
      await _loggingService.log('error', 'Failed to sync data', data: {'error': e.toString()});
      rethrow;
    } finally {
      isSyncing.value = false;
    }
  }

  // 检查同步状态
  Future<bool> checkSyncStatus() async {
    try {
      if (!_networkService.isConnected.value) return false;

      final lastSync = await _getLastSyncTime();
      if (lastSync == null) return true;

      final syncInterval = await _getSyncInterval();
      return DateTime.now().difference(lastSync) >= syncInterval;
    } catch (e) {
      await _loggingService.log('error', 'Failed to check sync status', data: {'error': e.toString()});
      return false;
    }
  }

  Future<Map<String, dynamic>> _collectSyncData() async {
    try {
      final lastSync = await _getLastSyncTime();
      
      return {
        'user_data': await _getModifiedData('user_data', lastSync),
        'settings': await _getModifiedData('app_settings', lastSync),
        'health_records': await _getModifiedData('health_records', lastSync),
        'life_records': await _getModifiedData('life_records', lastSync),
        'chat_history': await _getModifiedData('chat_history', lastSync),
      };
    } catch (e) {
      rethrow;
    }
  }

  Future<Map<String, dynamic>> _getModifiedData(String key, DateTime? since) async {
    try {
      final data = await _storageService.getLocal(key);
      if (data == null) return {};

      if (since == null) return data;

      // 过滤出修改时间晚于上次同步的数据
      return Map<String, dynamic>.from(data)..removeWhere((_, value) {
        final modifiedAt = DateTime.parse(value['updated_at'] ?? value['created_at']);
        return modifiedAt.isBefore(since);
      });
    } catch (e) {
      return {};
    }
  }

  Future<void> _uploadData(Map<String, dynamic> data) async {
    try {
      // TODO: 实现数据上传
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _downloadData() async {
    try {
      // TODO: 实现数据下载
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _mergeData() async {
    try {
      // TODO: 实现数据合并
    } catch (e) {
      rethrow;
    }
  }

  Future<DateTime?> _getLastSyncTime() async {
    try {
      final timeStr = await _storageService.getLocal('last_sync_time');
      return timeStr != null ? DateTime.parse(timeStr) : null;
    } catch (e) {
      return null;
    }
  }

  Future<Duration> _getSyncInterval() async {
    try {
      final settings = await _storageService.getLocal('sync_settings');
      final interval = settings?['sync_interval'] ?? 3600;
      return Duration(seconds: interval);
    } catch (e) {
      return const Duration(hours: 1);
    }
  }

  Future<void> _updateLastSyncTime() async {
    try {
      final now = DateTime.now();
      lastSyncTime.value = now;
      await _storageService.saveLocal('last_sync_time', now.toIso8601String());
    } catch (e) {
      rethrow;
    }
  }
} 