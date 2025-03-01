import '../../entities/health_data.dart';
import '../../repositories/health_repository.dart';

/// 同步外部健康数据用例
/// 用于从外部源（如Apple Health、Google Fit等）同步健康数据
class SyncExternalHealthDataUseCase {
  final HealthRepository _repository;

  SyncExternalHealthDataUseCase(this._repository);

  /// 执行用例
  /// 
  /// [userId] 用户ID
  /// [source] 数据源，如'apple_health', 'google_fit'等
  /// [startDate] 开始日期（可选）
  /// [endDate] 结束日期（可选）
  /// 
  /// 返回同步的健康数据列表
  Future<List<HealthData>> execute(
    String userId,
    String source, {
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    return _repository.syncExternalHealthData(
      userId,
      source,
      startDate: startDate,
      endDate: endDate,
    );
  }
} 