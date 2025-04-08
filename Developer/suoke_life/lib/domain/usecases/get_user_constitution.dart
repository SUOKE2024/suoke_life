import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/domain/entities/constitution_type.dart';
import 'package:suoke_life/domain/entities/constitution_type_result.dart';
import 'package:suoke_life/domain/repositories/user_constitution_repository.dart';
import 'package:suoke_life/di/providers/repository_providers.dart';

/// 获取用户体质相关信息的用例
class GetUserConstitutionUseCase {
  /// 用户体质仓库
  final UserConstitutionRepository _repository;
  
  /// 构造函数
  GetUserConstitutionUseCase(this._repository);
  
  /// 获取用户的最新体质评估结果
  Future<ConstitutionTypeResult?> getLatestAssessment(String userId) async {
    return _repository.getLatestAssessmentResult(userId);
  }
  
  /// 获取用户的历史体质评估结果
  Future<List<ConstitutionTypeResult>> getHistoricalAssessments(String userId) async {
    return _repository.getHistoricalAssessmentResults(userId);
  }
  
  /// 获取体质特征
  Future<ConstitutionTraits> getTraits(ConstitutionType type) async {
    return _repository.getConstitutionTraits(type);
  }
  
  /// 获取适宜食物
  Future<List<String>> getSuitableFoods(ConstitutionType type) async {
    return _repository.getSuitableFoods(type);
  }
  
  /// 获取不适宜食物
  Future<List<String>> getUnsuitableFoods(ConstitutionType type) async {
    return _repository.getUnsuitableFoods(type);
  }
  
  /// 根据体质类型获取个性化健康干预建议
  Future<Map<String, List<String>>> getPersonalizedSuggestions(
    String userId, 
    ConstitutionType type
  ) async {
    return _repository.getPersonalizedSuggestions(userId, type);
  }
  
  /// 开始新的体质评估
  Future<String> startNewAssessment(String userId) async {
    return _repository.startNewAssessment(userId);
  }
  
  /// 提交体质评估问卷答案
  Future<void> submitAssessmentAnswers(
    String assessmentId,
    Map<String, dynamic> answers
  ) async {
    return _repository.submitAssessmentAnswers(assessmentId, answers);
  }
  
  /// 获取体质评估问卷题目
  Future<List<Map<String, dynamic>>> getAssessmentQuestions() async {
    return _repository.getAssessmentQuestions();
  }
  
  /// 获取体质评估结果详情
  Future<ConstitutionTypeResult> getAssessmentResult(String assessmentId) async {
    return _repository.getAssessmentResult(assessmentId);
  }
}

/// 用户体质用例提供者
final getUserConstitutionUseCaseProvider = Provider<GetUserConstitutionUseCase>((ref) {
  final repository = ref.watch(userConstitutionRepositoryProvider);
  return GetUserConstitutionUseCase(repository);
}); 