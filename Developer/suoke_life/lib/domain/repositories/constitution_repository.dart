import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/domain/entities/constitution_data.dart';
import 'package:suoke_life/domain/entities/constitution_type.dart';
import 'package:suoke_life/domain/entities/constitution_type_result.dart';
import 'package:suoke_life/domain/entities/four_diagnostic_data.dart';

/// 体质存储库接口
///
/// 提供体质基本数据访问和管理功能
abstract class ConstitutionRepository {
  /// 获取所有体质类型特征
  Future<List<ConstitutionTraits>> getAllConstitutionTypes();
  
  /// 获取特定体质类型的特征
  Future<ConstitutionTraits> getConstitutionTraits(ConstitutionType type);
  
  /// 获取用户的体质识别结果
  Future<List<ConstitutionTypeResult>> getUserConstitutionResults(String userId);
  
  /// 保存用户体质识别结果
  Future<void> saveUserConstitutionResult(ConstitutionTypeResult result);
  
  /// 根据四诊数据生成体质识别结果
  Future<ConstitutionTypeResult> generateConstitutionResultFromDiagnosticData(
      String userId, String diagnosticDataId);
      
  /// 获取适合特定体质类型的食物列表
  Future<List<String>> getSuitableFoodsForConstitution(ConstitutionType type);
  
  /// 获取特定体质类型应避免的食物列表
  Future<List<String>> getUnsuitableFoodsForConstitution(ConstitutionType type);

  /// 获取适宜食物
  Future<List<String>> getSuitableFoods(ConstitutionType type);
  
  /// 获取不适宜食物
  Future<List<String>> getUnsuitableFoods(ConstitutionType type);
  
  /// 从四诊数据评估体质
  Future<ConstitutionTypeResult?> analyzeFromDiagnosticData(
    String userId,
    FourDiagnosticData diagnosticData
  );
}

/// 体质识别结果
class ConstitutionTypeResult {
  /// 结果ID
  final String id;
  
  /// 用户ID
  final String userId;
  
  /// 主要体质类型
  final ConstitutionType primaryType;
  
  /// 次要体质类型列表 (可能有多种混合体质)
  final List<ConstitutionType>? secondaryTypes;
  
  /// 平和体质评分 (0-100)
  final int balancedScore;
  
  /// 气虚体质评分 (0-100)
  final int qiDeficiencyScore;
  
  /// 阳虚体质评分 (0-100)
  final int yangDeficiencyScore;
  
  /// 阴虚体质评分 (0-100)
  final int yinDeficiencyScore;
  
  /// 痰湿体质评分 (0-100)
  final int phlegmDampnessScore;
  
  /// 湿热体质评分 (0-100)
  final int dampnessHeatScore;
  
  /// 血瘀体质评分 (0-100)
  final int bloodStasisScore;
  
  /// 气郁体质评分 (0-100)
  final int qiStagnationScore;
  
  /// 特禀体质评分 (0-100)
  final int specialConstitutionScore;
  
  /// 相关联的诊断数据ID
  final String? diagnosticDataId;
  
  /// 评估日期
  final DateTime assessmentDate;
  
  /// 评估结论
  final String conclusion;
  
  /// 体质改善建议
  final String? improvementSuggestions;
  
  /// 体质评估者ID
  final String? assessorId;
  
  /// 体质评估者姓名
  final String? assessorName;

  /// 创建体质识别结果
  ConstitutionTypeResult({
    required this.id,
    required this.userId,
    required this.primaryType,
    this.secondaryTypes,
    required this.balancedScore,
    required this.qiDeficiencyScore,
    required this.yangDeficiencyScore,
    required this.yinDeficiencyScore,
    required this.phlegmDampnessScore,
    required this.dampnessHeatScore,
    required this.bloodStasisScore,
    required this.qiStagnationScore,
    required this.specialConstitutionScore,
    this.diagnosticDataId,
    required this.assessmentDate,
    required this.conclusion,
    this.improvementSuggestions,
    this.assessorId,
    this.assessorName,
  });
  
  /// 从JSON创建实例
  factory ConstitutionTypeResult.fromJson(Map<String, dynamic> json) {
    return ConstitutionTypeResult(
      id: json['id'] as String,
      userId: json['userId'] as String,
      primaryType: ConstitutionType.values.firstWhere(
        (type) => type.toString() == 'ConstitutionType.${json['primaryType']}',
      ),
      secondaryTypes: json['secondaryTypes'] != null
          ? (json['secondaryTypes'] as List).map((e) => 
              ConstitutionType.values.firstWhere(
                (type) => type.toString() == 'ConstitutionType.$e',
              )
            ).toList()
          : null,
      balancedScore: json['balancedScore'] as int,
      qiDeficiencyScore: json['qiDeficiencyScore'] as int,
      yangDeficiencyScore: json['yangDeficiencyScore'] as int,
      yinDeficiencyScore: json['yinDeficiencyScore'] as int,
      phlegmDampnessScore: json['phlegmDampnessScore'] as int,
      dampnessHeatScore: json['dampnessHeatScore'] as int,
      bloodStasisScore: json['bloodStasisScore'] as int,
      qiStagnationScore: json['qiStagnationScore'] as int,
      specialConstitutionScore: json['specialConstitutionScore'] as int,
      diagnosticDataId: json['diagnosticDataId'] as String?,
      assessmentDate: DateTime.parse(json['assessmentDate'] as String),
      conclusion: json['conclusion'] as String,
      improvementSuggestions: json['improvementSuggestions'] as String?,
      assessorId: json['assessorId'] as String?,
      assessorName: json['assessorName'] as String?,
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'userId': userId,
      'primaryType': primaryType.toString().split('.').last,
      if (secondaryTypes != null) 
        'secondaryTypes': secondaryTypes!.map((e) => e.toString().split('.').last).toList(),
      'balancedScore': balancedScore,
      'qiDeficiencyScore': qiDeficiencyScore,
      'yangDeficiencyScore': yangDeficiencyScore,
      'yinDeficiencyScore': yinDeficiencyScore,
      'phlegmDampnessScore': phlegmDampnessScore,
      'dampnessHeatScore': dampnessHeatScore,
      'bloodStasisScore': bloodStasisScore,
      'qiStagnationScore': qiStagnationScore,
      'specialConstitutionScore': specialConstitutionScore,
      if (diagnosticDataId != null) 'diagnosticDataId': diagnosticDataId,
      'assessmentDate': assessmentDate.toIso8601String(),
      'conclusion': conclusion,
      if (improvementSuggestions != null) 'improvementSuggestions': improvementSuggestions,
      if (assessorId != null) 'assessorId': assessorId,
      if (assessorName != null) 'assessorName': assessorName,
    };
  }
}

/// 体质存储库provider
final constitutionRepositoryProvider = Provider<ConstitutionRepository>((ref) {
  throw UnimplementedError('ConstitutionRepository必须由数据层实现提供');
});
