import '../../entities/health_data.dart';
import '../../repositories/health_repository.dart';

/// 获取特定类型健康数据用例
/// 用于获取指定用户的特定类型健康数据
class GetHealthDataByTypeUseCase {
  final HealthRepository _repository;

  GetHealthDataByTypeUseCase(this._repository);

  /// 执行用例
  /// 
  /// [userId] 用户ID
  /// [type] 健康数据类型
  /// [startDate] 开始日期（可选）
  /// [endDate] 结束日期（可选）
  /// [limit] 限制返回数量
  /// [offset] 偏移量，用于分页
  /// 
  /// 返回特定类型的健康数据列表
  Future<List<HealthData>> execute(
    String userId,
    HealthDataType type, {
    DateTime? startDate,
    DateTime? endDate,
    int limit = 100,
    int offset = 0,
  }) async {
    return _repository.getHealthDataByType(
      userId,
      type,
      startDate: startDate,
      endDate: endDate,
      limit: limit,
      offset: offset,
    );
  }
} 