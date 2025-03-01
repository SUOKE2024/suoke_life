import '../../entities/health_data.dart';
import '../../repositories/health_repository.dart';

/// 获取每日健康汇总用例
/// 用于获取指定用户在特定日期的健康数据汇总
class GetDailyHealthSummaryUseCase {
  final HealthRepository _repository;

  GetDailyHealthSummaryUseCase(this._repository);

  /// 执行用例
  /// 
  /// [userId] 用户ID
  /// [date] 日期
  /// 
  /// 返回健康数据类型到数值的映射，表示每种类型的汇总值
  Future<Map<HealthDataType, num>> execute(String userId, DateTime date) async {
    return _repository.getDailyHealthSummary(userId, date);
  }
} 