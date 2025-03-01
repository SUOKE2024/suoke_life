import '../../entities/health_data.dart';
import '../../repositories/health_repository.dart';

/// 更新健康数据用例
/// 用于更新已存在的健康数据
class UpdateHealthDataUseCase {
  final HealthRepository _repository;

  UpdateHealthDataUseCase(this._repository);

  /// 执行用例
  /// 
  /// [data] 要更新的健康数据
  /// 
  /// 返回更新后的健康数据
  Future<HealthData> execute(HealthData data) async {
    return _repository.updateHealthData(data);
  }
} 