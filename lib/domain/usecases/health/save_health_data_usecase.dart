import '../../entities/health_data.dart';
import '../../repositories/health_repository.dart';

/// 保存健康数据用例
/// 用于保存新的健康数据
class SaveHealthDataUseCase {
  final HealthRepository _repository;

  SaveHealthDataUseCase(this._repository);

  /// 执行用例
  /// 
  /// [data] 要保存的健康数据
  /// 
  /// 返回保存后的健康数据（包含ID等服务器生成的字段）
  Future<HealthData> execute(HealthData data) async {
    return _repository.saveHealthData(data);
  }
  
  /// 批量保存健康数据
  /// 
  /// [dataList] 要保存的健康数据列表
  /// 
  /// 返回保存后的健康数据列表
  Future<List<HealthData>> executeBatch(List<HealthData> dataList) async {
    return _repository.saveBatchHealthData(dataList);
  }
} 