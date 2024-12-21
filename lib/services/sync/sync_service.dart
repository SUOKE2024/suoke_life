class SyncService extends GetxService {
  final _storage = Get.find<StorageService>();
  final _api = Get.find<ApiService>();
  
  // 增量同步
  Future<void> syncData() async {
    try {
      // 1. 获取上次同步时间
      final lastSync = await _storage.getLastSyncTime();
      
      // 2. 获取需要同步的本地数据
      final localChanges = await _storage.getChangesSince(lastSync);
      
      // 3. 上传本地变更到服务器
      await _api.uploadChanges(localChanges);
      
      // 4. 获取服务器端变更
      final serverChanges = await _api.getChangesSince(lastSync);
      
      // 5. 更新本地数据
      await _storage.applyServerChanges(serverChanges);
      
      // 6. 更新同步时间
      await _storage.updateLastSyncTime();
    } catch (e) {
      // 处理同步错误
    }
  }
} 