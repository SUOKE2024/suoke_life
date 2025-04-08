import 'package:suoke_life/domain/entities/constitution_type.dart';
import 'package:suoke_life/domain/entities/constitution_type_result.dart';
import 'package:suoke_life/domain/entities/four_diagnostic_data.dart';

/// 用户体质存储库接口
///
/// 提供用户体质评估相关的数据操作方法
abstract class UserConstitutionRepository {
  /// 获取用户最新的体质评估结果
  Future<ConstitutionTypeResult?> getLatestResult(String userId);
  
  /// 获取用户的历史体质评估结果
  Future<List<ConstitutionTypeResult>> getHistoricalResults(String userId);
  
  /// 获取特定体质类型的特征
  Future<ConstitutionTraits> getConstitutionTraits(ConstitutionType type);
  
  /// 获取适宜食物
  Future<List<String>> getSuitableFoods(ConstitutionType type);
  
  /// 获取不适宜食物
  Future<List<String>> getUnsuitableFoods(ConstitutionType type);
  
  /// 根据体质类型获取个性化健康干预建议
  Future<Map<String, List<String>>> getPersonalizedSuggestions(
    String userId, 
    ConstitutionType type
  );
  
  /// 开始新的体质评估
  ///
  /// 返回评估ID
  Future<String> createNewAssessment(String userId);
  
  /// 提交体质评估问卷答案
  Future<void> saveAssessmentAnswers(
    String assessmentId,
    Map<String, dynamic> answers
  );
  
  /// 获取体质评估问卷题目
  Future<List<Map<String, dynamic>>> getAssessmentQuestions();
  
  /// 获取体质评估结果详情
  Future<ConstitutionTypeResult?> getAssessmentResult(String assessmentId);
  
  /// 根据四诊数据评估体质
  Future<ConstitutionTypeResult?> analyzeFromDiagnosticData(
    String userId,
    FourDiagnosticData diagnosticData
  );
  
  /// 保存体质评估结果
  Future<void> saveAssessmentResult(ConstitutionTypeResult result);
  
  /// 更新用户主要体质类型
  Future<void> updateUserMainConstitutionType(
    String userId,
    ConstitutionType mainType
  );
  
  /// 获取所有体质类型的信息
  Future<List<ConstitutionTraits>> getAllConstitutionTypes();
} 