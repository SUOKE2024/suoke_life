@singleton
class DataCleanupService {
  final LocalStorageService _storage;
  
  DataCleanupService(this._storage);

  Future<void> cleanupExpiredData() async {
    final now = DateTime.now();
    
    for (final type in PrivacyDataTypes.values) {
      final data = await _storage.getPrivateData(type);
      if (data == null) continue;

      final retentionPeriod = CachePolicy.getRetentionPeriod(type);
      final expiryDate = now.subtract(retentionPeriod);

      // 清理过期数据
      final cleanedData = data.where((item) {
        final timestamp = DateTime.parse(item['timestamp']);
        return timestamp.isAfter(expiryDate);
      }).toList();

      await _storage.savePrivateData(type, {'items': cleanedData});
    }
  }

  Future<void> clearUserData() async {
    // 用户注销时清理所有私密数据
    for (final type in PrivacyDataTypes.values) {
      await _storage.deletePrivateData(type);
    }
  }
} 