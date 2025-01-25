import 'package:injectable/injectable.dart';
import '../network/network_service.dart';
import '../storage/local_storage.dart';
import '../logger/logger.dart';
import '../network/connectivity_service.dart';

@singleton
class SyncService {
  final NetworkService _network;
  final LocalStorage _storage;
  final ConnectivityService _connectivity;
  final AppLogger _logger;

  SyncService(
    this._network,
    this._storage,
    this._connectivity,
    this._logger,
  );

  Future<void> syncData() async {
    if (!await _connectivity.checkConnectivity()) {
      _logger.info('No internet connection, skipping sync');
      return;
    }

    try {
      // 获取上次同步时间
      final lastSync = await _getLastSyncTime();
      
      // 获取需要同步的数据
      final pendingData = await _getPendingData(lastSync);
      if (pendingData.isEmpty) {
        _logger.info('No data to sync');
        return;
      }

      // 上传数据到服务器
      await _uploadData(pendingData);

      // 获取服务器更新
      await _fetchServerUpdates(lastSync);

      // 更新同步时间
      await _updateLastSyncTime();
    } catch (e, stack) {
      _logger.error('Error during sync', e, stack);
      rethrow;
    }
  }

  Future<DateTime?> _getLastSyncTime() async {
    final timestamp = await _storage.getString('last_sync_time');
    return timestamp != null ? DateTime.parse(timestamp) : null;
  }

  Future<List<Map<String, dynamic>>> _getPendingData(DateTime? lastSync) async {
    final pendingData = <Map<String, dynamic>>[];
    
    // 获取各类型的待同步数据
    pendingData.addAll(await _getPendingHealthData(lastSync));
    pendingData.addAll(await _getPendingAgricultureData(lastSync));
    pendingData.addAll(await _getPendingUserData(lastSync));

    return pendingData;
  }

  Future<List<Map<String, dynamic>>> _getPendingHealthData(
    DateTime? lastSync,
  ) async {
    // 实现健康数据同步逻辑
    return [];
  }

  Future<List<Map<String, dynamic>>> _getPendingAgricultureData(
    DateTime? lastSync,
  ) async {
    // 实现农业数据同步逻辑
    return [];
  }

  Future<List<Map<String, dynamic>>> _getPendingUserData(
    DateTime? lastSync,
  ) async {
    // 实现用户数据同步逻辑
    return [];
  }

  Future<void> _uploadData(List<Map<String, dynamic>> data) async {
    await _network.post('/sync/upload', {'data': data});
  }

  Future<void> _fetchServerUpdates(DateTime? lastSync) async {
    final updates = await _network.get(
      '/sync/updates',
      params: {
        if (lastSync != null) 'since': lastSync.toIso8601String(),
      },
    );

    // 处理服务器更新
    await _processServerUpdates(updates);
  }

  Future<void> _processServerUpdates(Map<String, dynamic> updates) async {
    // 实现更新处理逻辑
  }

  Future<void> _updateLastSyncTime() async {
    await _storage.setString(
      'last_sync_time',
      DateTime.now().toIso8601String(),
    );
  }
} 