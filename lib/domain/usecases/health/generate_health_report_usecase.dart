import '../../repositories/health_repository.dart';

/// 生成健康报告用例
/// 用于生成用户在特定时间段内的健康报告
class GenerateHealthReportUseCase {
  final HealthRepository _repository;

  GenerateHealthReportUseCase(this._repository);

  /// 执行用例
  /// 
  /// [userId] 用户ID
  /// [startDate] 开始日期
  /// [endDate] 结束日期
  /// 
  /// 返回健康报告数据
  Future<Map<String, dynamic>> execute(
    String userId, {
    required DateTime startDate,
    required DateTime endDate,
  }) async {
    return _repository.generateHealthReport(
      userId,
      startDate: startDate,
      endDate: endDate,
    );
  }
} 