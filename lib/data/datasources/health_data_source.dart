import '../models/health_data_model.dart';
import '../../domain/entities/health_data.dart';

/// 健康数据源接口
/// 定义健康数据的获取和持久化方法
abstract class HealthDataSource {
  /// 获取用户的所有健康数据
  Future<List<HealthDataModel>> getUserHealthData(
    String userId, {
    DateTime? startDate,
    DateTime? endDate,
    int limit = 100,
    int offset = 0,
  });
  
  /// 获取特定类型的健康数据
  Future<List<HealthDataModel>> getHealthDataByType(
    String userId,
    HealthDataType type, {
    DateTime? startDate,
    DateTime? endDate,
    int limit = 100,
    int offset = 0,
  });
  
  /// 通过ID获取健康数据
  Future<HealthDataModel> getHealthDataById(String dataId);
  
  /// 保存新的健康数据
  Future<HealthDataModel> saveHealthData(HealthDataModel data);
  
  /// 批量保存健康数据
  Future<List<HealthDataModel>> saveBatchHealthData(List<HealthDataModel> dataList);
  
  /// 更新健康数据
  Future<HealthDataModel> updateHealthData(HealthDataModel data);
  
  /// 删除健康数据
  Future<void> deleteHealthData(String dataId);
  
  /// 批量删除健康数据
  Future<void> deleteBatchHealthData(List<String> dataIds);
  
  /// 获取特定日期的健康数据汇总
  Future<Map<HealthDataType, num>> getDailyHealthSummary(
    String userId,
    DateTime date,
  );
  
  /// 获取特定时间段的健康数据统计
  Future<Map<String, dynamic>> getHealthStatistics(
    String userId,
    HealthDataType type, {
    required DateTime startDate,
    required DateTime endDate,
    String? groupBy, // 'day', 'week', 'month'
  });
  
  /// 获取最近的健康数据记录
  Future<HealthDataModel?> getLatestHealthData(
    String userId,
    HealthDataType type,
  );
  
  /// 获取健康数据趋势
  Future<List<Map<String, dynamic>>> getHealthTrend(
    String userId,
    HealthDataType type, {
    required DateTime startDate,
    required DateTime endDate,
    required String interval, // 'hour', 'day', 'week', 'month'
  });
  
  /// 同步第三方健康数据
  Future<List<HealthDataModel>> syncExternalHealthData(
    String userId,
    String source, {
    DateTime? startDate,
    DateTime? endDate,
  });
} 