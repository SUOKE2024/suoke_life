import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/domain/entities/constitution_type.dart';
import 'package:suoke_life/domain/entities/health_regimen.dart';

/// 健康调理方案存储库接口
///
/// 定义中医健康调理方案的存储和查询操作
abstract class HealthRegimenRepository {
  /// 保存健康调理方案
  Future<void> saveHealthRegimen(HealthRegimen regimen);
  
  /// 通过ID获取健康调理方案
  Future<HealthRegimen> getHealthRegimenById(String id);
  
  /// 获取用户的所有健康调理方案
  Future<List<HealthRegimen>> getUserHealthRegimens(String userId);
  
  /// 获取用户最新的健康调理方案
  Future<HealthRegimen?> getLatestHealthRegimen(String userId);
  
  /// 删除健康调理方案
  Future<void> deleteHealthRegimen(String id);
  
  /// 根据体质类型获取调理方案
  Future<HealthRegimen> generateHealthRegimenByConstitution(
      String userId, ConstitutionType constitutionType, String diagnosis);
  
  /// 根据四诊数据生成健康调理方案
  Future<HealthRegimen> generateHealthRegimenFromDiagnosticData(
      String userId, String diagnosticDataId);
      
  /// 获取适合特定体质的食疗方案
  Future<List<MedicinalDietItem>> getMedicinalDietForConstitution(ConstitutionType type);
  
  /// 获取适合特定体质的传统功法
  Future<List<TraditionalExercise>> getTraditionalExercisesForConstitution(ConstitutionType type);
  
  /// 获取适合特定体质的穴位按摩方案
  Future<List<AcupointRecommendation>> getAcupointRecommendationsForConstitution(
      ConstitutionType type);
      
  /// 获取季节性调理建议
  Future<Map<String, dynamic>> getSeasonalRegimenSuggestions(
      ConstitutionType type, String season);
      
  /// 保存用户对方案的反馈
  Future<void> saveRegimenFeedback(String regimenId, String feedback, int rating);
  
  /// 获取用户方案执行的依从性数据
  Future<Map<String, dynamic>> getRegimenAdherenceData(String userId, String regimenId);
}

/// 健康调理方案存储库provider
final healthRegimenRepositoryProvider = Provider<HealthRegimenRepository>((ref) {
  throw UnimplementedError('HealthRegimenRepository必须由数据层实现提供');
}); 