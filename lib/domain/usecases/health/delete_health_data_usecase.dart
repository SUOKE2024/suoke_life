import '../../repositories/health_repository.dart';

/// 删除健康数据用例
/// 用于删除指定ID的健康数据
class DeleteHealthDataUseCase {
  final HealthRepository _repository;

  DeleteHealthDataUseCase(this._repository);

  /// 执行用例
  /// 
  /// [dataId] 要删除的健康数据ID
  Future<void> execute(String dataId) async {
    return _repository.deleteHealthData(dataId);
  }
  
  /// 批量删除健康数据
  /// 
  /// [dataIds] 要删除的健康数据ID列表
  Future<void> executeBatch(List<String> dataIds) async {
    return _repository.deleteBatchHealthData(dataIds);
  }
} 