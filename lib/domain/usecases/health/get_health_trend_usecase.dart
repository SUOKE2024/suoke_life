import '../../entities/health_data.dart';
import '../../repositories/health_repository.dart';

/// 获取健康趋势用例
/// 用于获取指定用户特定类型健康数据的趋势
class GetHealthTrendUseCase {
  final HealthRepository _repository;

  GetHealthTrendUseCase(this._repository);

  /// 执行用例
  /// 
  /// [userId] 用户ID
  /// [type] 健康数据类型
  /// [startDate] 开始日期
  /// [endDate] 结束日期
  /// [interval] 时间间隔，如'hour', 'day', 'week', 'month'
  /// 
  /// 返回健康数据趋势
  Future<List<Map<String, dynamic>>> execute(
    String userId,
    HealthDataType type, {
    required DateTime startDate,
    required DateTime endDate,
    required String interval,
  }) async {
    return _repository.getHealthTrend(
      userId,
      type,
      startDate: startDate,
      endDate: endDate,
      interval: interval,
    );
  }
} 