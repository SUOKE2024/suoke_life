import '../../entities/health_data.dart';
import '../../repositories/health_repository.dart';

/// 获取健康数据详情用例
/// 用于获取指定ID的健康数据详情
class GetHealthDataByIdUseCase {
  final HealthRepository _repository;

  GetHealthDataByIdUseCase(this._repository);

  /// 执行用例
  /// 
  /// [dataId] 健康数据ID
  /// 
  /// 返回健康数据详情
  Future<HealthData> execute(String dataId) async {
    return _repository.getHealthDataById(dataId);
  }
} 