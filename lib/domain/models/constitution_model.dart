import 'package:equatable/equatable.dart';

/// 体质类型枚举
enum ConstitutionType {
  balanced, // 平和质
  qiDeficiency, // 气虚质
  yangDeficiency, // 阳虚质
  yinDeficiency, // 阴虚质
  phlegmDampness, // 痰湿质
  dampnessHeat, // 湿热质
  bloodStasis, // 血瘀质
  qiStagnation, // 气郁质
  specialDiathesis, // 特禀质
}

/// 体质类型扩展方法
extension ConstitutionTypeExtension on ConstitutionType {
  /// 获取体质类型名称
  String get name {
    switch (this) {
      case ConstitutionType.balanced:
        return '平和质';
      case ConstitutionType.qiDeficiency:
        return '气虚质';
      case ConstitutionType.yangDeficiency:
        return '阳虚质';
      case ConstitutionType.yinDeficiency:
        return '阴虚质';
      case ConstitutionType.phlegmDampness:
        return '痰湿质';
      case ConstitutionType.dampnessHeat:
        return '湿热质';
      case ConstitutionType.bloodStasis:
        return '血瘀质';
      case ConstitutionType.qiStagnation:
        return '气郁质';
      case ConstitutionType.specialDiathesis:
        return '特禀质';
    }
  }

  /// 获取体质类型描述
  String get description {
    switch (this) {
      case ConstitutionType.balanced:
        return '体格匀称健壮，面色红润，精力充沛，性格平和，抗病能力强';
      case ConstitutionType.qiDeficiency:
        return '疲乏无力，气短懒言，容易出汗，舌淡苔白，脉弱';
      case ConstitutionType.yangDeficiency:
        return '怕冷，手足不温，面色偏白，喜温热，小便清长，舌淡胖，脉沉迟';
      case ConstitutionType.yinDeficiency:
        return '手足心热，口干咽燥，面色偏红，舌红少津，脉细数';
      case ConstitutionType.phlegmDampness:
        return '体形肥胖，面部皮脂较多，胸闷痰多，舌苔厚腻，脉滑';
      case ConstitutionType.dampnessHeat:
        return '面垢油光，口苦口臭，大便粘滞不爽，小便黄赤，舌红苔黄腻';
      case ConstitutionType.bloodStasis:
        return '肤色晦暗，面部或舌有瘀点，口唇黯淡，舌质紫暗或有瘀斑，脉涩';
      case ConstitutionType.qiStagnation:
        return '情绪波动明显，焦虑忧郁，舌苔薄白，脉弦';
      case ConstitutionType.specialDiathesis:
        return '过敏体质，容易对特定物质或环境产生异常反应';
    }
  }

  /// 获取体质类型养生建议
  String get healthAdvice {
    switch (this) {
      case ConstitutionType.balanced:
        return '保持规律作息，均衡饮食，适度运动，调节情绪';
      case ConstitutionType.qiDeficiency:
        return '饮食宜温热，多食补气食物，避免过度劳累，保持充足睡眠';
      case ConstitutionType.yangDeficiency:
        return '注意保暖，适度进行阳光浴，饮食宜温热，避免生冷食物';
      case ConstitutionType.yinDeficiency:
        return '避免辛辣刺激食物，保持充足睡眠，心态平和，多食滋阴润燥食物';
      case ConstitutionType.phlegmDampness:
        return '饮食清淡，控制油脂摄入，适量运动，避免过度饮酒';
      case ConstitutionType.dampnessHeat:
        return '饮食清淡，避免辛辣油腻食物，多饮水，保持大便通畅';
      case ConstitutionType.bloodStasis:
        return '保持情绪稳定，适度运动，饮食宜清淡，避免过食油腻';
      case ConstitutionType.qiStagnation:
        return '保持心情舒畅，适当参加户外活动，学习情绪管理技巧';
      case ConstitutionType.specialDiathesis:
        return '避免接触过敏原，注意饮食卫生，保持室内通风，增强免疫力';
    }
  }
}

/// 体质评估结果模型
class ConstitutionResult extends Equatable {
  final DateTime assessmentDate;
  final Map<ConstitutionType, double> scores;
  final ConstitutionType primaryType;
  final List<ConstitutionType> secondaryTypes;
  final String? remark;

  const ConstitutionResult({
    required this.assessmentDate,
    required this.scores,
    required this.primaryType,
    required this.secondaryTypes,
    this.remark,
  });

  /// 从JSON转换为体质评估结果对象
  factory ConstitutionResult.fromJson(Map<String, dynamic> json) {
    final Map<ConstitutionType, double> scores = {};
    final Map<String, dynamic> jsonScores = json['scores'];

    for (var entry in jsonScores.entries) {
      scores[_stringToConstitutionType(entry.key)] = entry.value;
    }

    final List<ConstitutionType> secondaryTypes = [];
    final List<dynamic> jsonSecondaryTypes = json['secondary_types'];

    for (var typeStr in jsonSecondaryTypes) {
      secondaryTypes.add(_stringToConstitutionType(typeStr));
    }

    return ConstitutionResult(
      assessmentDate: DateTime.parse(json['assessment_date']),
      scores: scores,
      primaryType: _stringToConstitutionType(json['primary_type']),
      secondaryTypes: secondaryTypes,
      remark: json['remark'],
    );
  }

  /// 转换为JSON
  Map<String, dynamic> toJson() {
    final Map<String, dynamic> jsonScores = {};

    for (var entry in scores.entries) {
      jsonScores[entry.key.toString()] = entry.value;
    }

    final List<String> jsonSecondaryTypes = [];

    for (var type in secondaryTypes) {
      jsonSecondaryTypes.add(type.toString());
    }

    return {
      'assessment_date': assessmentDate.toIso8601String(),
      'scores': jsonScores,
      'primary_type': primaryType.toString(),
      'secondary_types': jsonSecondaryTypes,
      'remark': remark,
    };
  }

  /// 字符串转体质类型
  static ConstitutionType _stringToConstitutionType(String typeStr) {
    return ConstitutionType.values.firstWhere(
      (type) => type.toString() == typeStr,
      orElse: () => ConstitutionType.balanced,
    );
  }

  /// 用于相等性比较
  @override
  List<Object?> get props => [
        assessmentDate,
        scores,
        primaryType,
        secondaryTypes,
        remark,
      ];
}
