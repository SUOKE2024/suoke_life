class DataUploadService extends GetxService {
  final _storage = Get.find<StorageService>();
  final _api = Get.find<ApiService>();
  
  // 数据脱敏和上传
  Future<void> uploadAnonymousData() async {
    try {
      // 1. 获取用户是否同意数据共享
      final hasConsent = await _storage.getDataSharingConsent();
      if (!hasConsent) return;

      // 2. 获取需要上传的数据
      final rawData = await _storage.getHealthData();
      
      // 3. 数据脱敏处理
      final anonymizedData = await _anonymizeData(rawData);
      
      // 4. 上传匿名数据
      await _api.uploadDataset(anonymizedData);
      
    } catch (e) {
      print('数据上传失败: $e');
    }
  }

  // 数据脱敏处理
  Future<Map<String, dynamic>> _anonymizeData(Map<String, dynamic> data) async {
    // 移除个人标识信息
    final anonymized = Map<String, dynamic>.from(data)
      ..remove('name')
      ..remove('phone')
      ..remove('idCard')
      ..remove('address');
      
    // 替换为统计区间
    if (anonymized.containsKey('age')) {
      anonymized['ageRange'] = _getAgeRange(anonymized['age']);
      anonymized.remove('age');
    }
    
    return anonymized;
  }
} 