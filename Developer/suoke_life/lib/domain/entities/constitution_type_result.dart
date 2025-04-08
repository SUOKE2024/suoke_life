import 'package:suoke_life/domain/entities/constitution_type.dart';

/// 体质类型评估结果
///
/// 存储体质评估的详细信息，包括主体质类型、次要体质类型、分数和诊断结论
class ConstitutionTypeResult {
  /// 结果ID
  final String id;
  
  /// 用户ID
  final String userId;
  
  /// 评估日期
  final DateTime assessmentDate;
  
  /// 主体质类型
  final ConstitutionType mainType;
  
  /// 主体质类型分数（0-100）
  final double mainTypeScore;
  
  /// 次要体质类型列表
  final List<ConstitutionType> secondaryTypes;
  
  /// 次要体质类型分数
  final Map<ConstitutionType, double> secondaryTypeScores;
  
  /// 所有体质类型的分数
  final Map<ConstitutionType, double> allTypeScores;
  
  /// 诊断结论
  final String conclusion;
  
  /// 改善建议
  final Map<String, List<String>> improvementSuggestions;
  
  /// 是否为AI生成的结果
  final bool isAiGenerated;
  
  /// 数据来源（问卷/四诊合参/AI推断）
  final ConstitutionResultSource source;
  
  /// 创建体质类型评估结果
  ConstitutionTypeResult({
    required this.id,
    required this.userId,
    required this.assessmentDate,
    required this.mainType,
    required this.mainTypeScore,
    required this.secondaryTypes,
    required this.secondaryTypeScores,
    required this.allTypeScores,
    required this.conclusion,
    required this.improvementSuggestions,
    this.isAiGenerated = false,
    this.source = ConstitutionResultSource.questionnaire,
  });
  
  /// 将JSON转换为体质类型评估结果对象
  factory ConstitutionTypeResult.fromJson(Map<String, dynamic> json) {
    // 解析体质类型
    final mainType = _parseConstitutionType(json['mainType']);
    
    // 解析次要体质类型列表
    final secondaryTypes = (json['secondaryTypes'] as List<dynamic>)
        .map((type) => _parseConstitutionType(type))
        .toList();
    
    // 解析次要体质类型分数
    final Map<ConstitutionType, double> secondaryTypeScores = {};
    (json['secondaryTypeScores'] as Map<String, dynamic>).forEach((key, value) {
      secondaryTypeScores[_parseConstitutionType(key)] = (value as num).toDouble();
    });
    
    // 解析所有体质类型分数
    final Map<ConstitutionType, double> allTypeScores = {};
    (json['allTypeScores'] as Map<String, dynamic>).forEach((key, value) {
      allTypeScores[_parseConstitutionType(key)] = (value as num).toDouble();
    });
    
    // 解析改善建议
    final Map<String, List<String>> improvementSuggestions = {};
    (json['improvementSuggestions'] as Map<String, dynamic>).forEach((key, value) {
      improvementSuggestions[key] = (value as List<dynamic>).cast<String>();
    });
    
    return ConstitutionTypeResult(
      id: json['id'],
      userId: json['userId'],
      assessmentDate: DateTime.parse(json['assessmentDate']),
      mainType: mainType,
      mainTypeScore: (json['mainTypeScore'] as num).toDouble(),
      secondaryTypes: secondaryTypes,
      secondaryTypeScores: secondaryTypeScores,
      allTypeScores: allTypeScores,
      conclusion: json['conclusion'],
      improvementSuggestions: improvementSuggestions,
      isAiGenerated: json['isAiGenerated'] ?? false,
      source: _parseResultSource(json['source'] ?? 'questionnaire'),
    );
  }
  
  /// 将体质类型评估结果对象转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'userId': userId,
      'assessmentDate': assessmentDate.toIso8601String(),
      'mainType': mainType.name,
      'mainTypeScore': mainTypeScore,
      'secondaryTypes': secondaryTypes.map((type) => type.name).toList(),
      'secondaryTypeScores': secondaryTypeScores.map(
        (key, value) => MapEntry(key.name, value),
      ),
      'allTypeScores': allTypeScores.map(
        (key, value) => MapEntry(key.name, value),
      ),
      'conclusion': conclusion,
      'improvementSuggestions': improvementSuggestions,
      'isAiGenerated': isAiGenerated,
      'source': source.name,
    };
  }
  
  /// 复制体质类型评估结果并修改部分属性
  ConstitutionTypeResult copyWith({
    String? id,
    String? userId,
    DateTime? assessmentDate,
    ConstitutionType? mainType,
    double? mainTypeScore,
    List<ConstitutionType>? secondaryTypes,
    Map<ConstitutionType, double>? secondaryTypeScores,
    Map<ConstitutionType, double>? allTypeScores,
    String? conclusion,
    Map<String, List<String>>? improvementSuggestions,
    bool? isAiGenerated,
    ConstitutionResultSource? source,
  }) {
    return ConstitutionTypeResult(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      assessmentDate: assessmentDate ?? this.assessmentDate,
      mainType: mainType ?? this.mainType,
      mainTypeScore: mainTypeScore ?? this.mainTypeScore,
      secondaryTypes: secondaryTypes ?? this.secondaryTypes,
      secondaryTypeScores: secondaryTypeScores ?? this.secondaryTypeScores,
      allTypeScores: allTypeScores ?? this.allTypeScores,
      conclusion: conclusion ?? this.conclusion,
      improvementSuggestions: improvementSuggestions ?? this.improvementSuggestions,
      isAiGenerated: isAiGenerated ?? this.isAiGenerated,
      source: source ?? this.source,
    );
  }
  
  /// 解析体质类型
  static ConstitutionType _parseConstitutionType(String typeName) {
    return ConstitutionType.values.firstWhere(
      (type) => type.name == typeName,
      orElse: () => ConstitutionType.balanced,
    );
  }
  
  /// 解析结果来源
  static ConstitutionResultSource _parseResultSource(String sourceName) {
    return ConstitutionResultSource.values.firstWhere(
      (source) => source.name == sourceName,
      orElse: () => ConstitutionResultSource.questionnaire,
    );
  }
}

/// 体质评估结果来源
enum ConstitutionResultSource {
  /// 问卷调查
  questionnaire,
  
  /// 四诊合参
  fourDiagnostic,
  
  /// AI推断
  aiInference,
} 