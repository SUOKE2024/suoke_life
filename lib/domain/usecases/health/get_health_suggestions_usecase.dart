import '../../entities/health_data.dart';
import '../../repositories/health_repository.dart';

/// 获取健康建议用例
/// 用于获取基于用户健康数据的个性化建议
class GetHealthSuggestionsUseCase {
  final HealthRepository _repository;

  GetHealthSuggestionsUseCase(this._repository);

  /// 执行用例
  /// 
  /// [userId] 用户ID
  /// [focusArea] 关注的健康领域（可选）
  /// 
  /// 返回健康建议列表
  Future<List<String>> execute(String userId, {HealthDataType? focusArea}) async {
    return _repository.getHealthSuggestions(userId, focusArea: focusArea);
  }
} 