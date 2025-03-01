import '../../entities/health_data.dart';
import '../../repositories/health_repository.dart';

/// 获取最新健康数据用例
/// 用于获取指定用户特定类型的最新健康数据
class GetLatestHealthDataUseCase {
  final HealthRepository _repository;

  GetLatestHealthDataUseCase(this._repository);

  /// 执行用例
  /// 
  /// [userId] 用户ID
  /// [type] 健康数据类型
  /// 
  /// 返回最新的健康数据，如果不存在则返回null
  Future<HealthData?> execute(String userId, HealthDataType type) async {
    return _repository.getLatestHealthData(userId, type);
  }
} 