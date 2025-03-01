import '../../entities/health_data.dart';
import '../../repositories/health_repository.dart';

/// 获取健康数据统计用例
/// 用于获取指定用户特定类型健康数据的统计信息
class GetHealthStatisticsUseCase {
  final HealthRepository _repository;

  GetHealthStatisticsUseCase(this._repository);

  /// 执行用例
  /// 
  /// [userId] 用户ID
  /// [type] 健康数据类型
  /// [startDate] 开始日期
  /// [endDate] 结束日期
  /// [groupBy] 分组方式，如'day', 'week', 'month'
  /// 
  /// 返回健康数据统计信息
  Future<Map<String, dynamic>> execute(
    String userId,
    HealthDataType type, {
    required DateTime startDate,
    required DateTime endDate,
    String? groupBy,
  }) async {
    return _repository.getHealthStatistics(
      userId,
      type,
      startDate: startDate,
      endDate: endDate,
      groupBy: groupBy,
    );
  }
} 