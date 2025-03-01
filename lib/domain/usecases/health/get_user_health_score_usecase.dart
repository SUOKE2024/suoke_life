import '../../repositories/health_repository.dart';

/// 获取用户健康评分用例
/// 用于计算用户的综合健康评分
class GetUserHealthScoreUseCase {
  final HealthRepository _repository;

  GetUserHealthScoreUseCase(this._repository);

  /// 执行用例
  /// 
  /// [userId] 用户ID
  /// 
  /// 返回用户健康评分信息
  Future<Map<String, dynamic>> execute(String userId) async {
    return _repository.getUserHealthScore(userId);
  }
} 