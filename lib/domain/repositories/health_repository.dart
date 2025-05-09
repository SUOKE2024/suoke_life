import 'package:suoke_life/domain/models/health_record_model.dart';

/// 健康数据仓库接口
abstract class HealthRepository {
  /// 获取用户所有健康记录
  Future<List<HealthRecord>> getAllRecords(String userId);

  /// 根据类型获取用户健康记录
  Future<List<HealthRecord>> getRecordsByType(
      String userId, HealthDataType type);

  /// 获取用户最近指定数量的健康记录
  Future<List<HealthRecord>> getRecentRecords(String userId, int limit,
      {HealthDataType? type});

  /// 根据日期范围获取用户健康记录
  Future<List<HealthRecord>> getRecordsByDateRange(
      String userId, DateTime startDate, DateTime endDate,
      {HealthDataType? type});

  /// 添加健康记录
  Future<HealthRecord> addRecord(HealthRecord record);

  /// 根据ID获取单条健康记录
  Future<HealthRecord?> getRecordById(String id);

  /// 更新健康记录
  Future<HealthRecord> updateRecord(HealthRecord record);

  /// 删除健康记录
  Future<bool> deleteRecord(String id);

  /// 获取指定类型的最新一条记录
  Future<HealthRecord?> getLatestRecord(String userId, HealthDataType type);

  /// 获取健康数据统计信息（如平均值、最高值等）
  Future<Map<String, dynamic>> getStatistics(
    String userId,
    HealthDataType type,
    DateTime startDate,
    DateTime endDate,
  );
}
