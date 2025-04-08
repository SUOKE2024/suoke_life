/// 健康数据存储库接口
abstract class HealthDataRepository {
  /// 获取用户健康数据
  Future<Map<String, dynamic>> getUserHealthData(String userId);

  /// 保存健康数据
  Future<bool> saveHealthData(String userId, Map<String, dynamic> data);

  /// 同步健康数据
  Future<bool> syncHealthData(String userId);

  /// 获取环境健康数据
  Future<Map<String, dynamic>> getEnvironmentalHealthData();
}
