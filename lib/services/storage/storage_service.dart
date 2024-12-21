class StorageService extends GetxService {
  // 写入数据时同时更新本地和远程
  Future<void> saveData(String key, dynamic data) async {
    try {
      // 1. 先保存到本地
      await Hive.box('data').put(key, data);
      
      // 2. 标记需要同步
      await _markForSync(key);
      
      // 3. 如果在线则立即同步
      if (await _isOnline()) {
        await Get.find<SyncService>().syncData();
      }
    } catch (e) {
      // 处理错误
    }
  }
} 