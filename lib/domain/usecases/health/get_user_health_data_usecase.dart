import '../../entities/health_data.dart';
import '../../repositories/health_repository.dart';

/// 获取用户健康数据用例
/// 用于获取指定用户的所有健康数据
class GetUserHealthDataUseCase {
  final HealthRepository _repository;

  GetUserHealthDataUseCase(this._repository);

  /// 执行用例
  /// 
  /// [userId] 用户ID
  /// [startDate] 开始日期（可选）
  /// [endDate] 结束日期（可选）
  /// [limit] 限制返回数量
  /// [offset] 偏移量，用于分页
  /// 
  /// 返回用户健康数据列表
  Future<List<HealthData>> execute(
    String userId, {
    DateTime? startDate,
    DateTime? endDate,
    int limit = 100,
    int offset = 0,
  }) async {
    return _repository.getUserHealthData(
      userId,
      startDate: startDate,
      endDate: endDate,
      limit: limit,
      offset: offset,
    );
  }
} 