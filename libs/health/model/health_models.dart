import 'package:json_annotation/json_annotation.dart';

part 'health_models.g.dart';

// 健康评估核心模型
@JsonSerializable()
class HealthAssessment {
  final TCMConstitution constitution;
  final List<HealthRisk> riskFactors;
  final List<HealthRecommendation> recommendations;

  const HealthAssessment({
    required this.constitution,
    required this.riskFactors,
    required this.recommendations,
  });
}

// 健康推荐标准模型
@JsonSerializable()
class HealthRecommendation {
  final String category;
  final String description;
  final String rationale;
  final DateTime effectiveDate;

  const HealthRecommendation({
    required this.category,
    required this.description,
    required this.rationale,
    required this.effectiveDate,
  });
}

// 健康风险量化模型
@JsonSerializable()
class HealthRisk {
  final String riskFactor;
  final double probability;
  final SeverityLevel severity;
  
  const HealthRisk({
    required this.riskFactor,
    required this.probability,
    required this.severity,
  });
}

enum SeverityLevel { low, medium, high, critical }

// 扩展原有生物信号模型
@JsonSerializable()
class BiologicalSignals {
  final ImageData tongueImage;
  final PulseData pulseWaveform;
  final double bodyTemperature; // 新增体温监测
  final double skinHumidity;    // 新增皮肤湿度
  
  // 原有字段保持不变...
}

// 新增农历节气模型
@JsonSerializable()
class LunarTerm {
  final String termName;
  final DateTime startDate;
  final List<String> healthTips;
  final List<String> recommendedFoods;
  
  const LunarTerm({
    required this.termName,
    required this.startDate,
    required this.healthTips,
    required this.recommendedFoods,
  });
}

// 新增中医辨证模型
@JsonSerializable()
class TCMDiagnosis {
  final String bodyConstitution; // 体质类型
  final List<String> acupuncturePoints; // 推荐穴位
  final List<String> herbalRecommendations; // 中药建议
  final String dietaryGuidance; // 饮食指导
  final List<String> foodTherapyAdvice; // 新增食疗建议
  
  const TCMDiagnosis({
    required this.bodyConstitution,
    required this.acupuncturePoints,
    required this.herbalRecommendations,
    required this.dietaryGuidance,
    required this.foodTherapyAdvice, // 新增参数
  });
}

@JsonSerializable()
class DailyHealthPlan {
  final DietPlan diet;
  final ExercisePlan exercise;
  final List<HealthReminder> reminders;
  final TCMTherapy tcmTherapy;
  final List<String> mentalHealthAdvice;
  final List<AgriculturalProduct> recommendedProducts;
  final List<String> tcmDietaryAdvice; // 新增食疗建议字段

  const DailyHealthPlan({
    required this.diet,
    required this.exercise,
    required this.reminders,
    required this.tcmTherapy,
    required this.mentalHealthAdvice,
    required this.recommendedProducts,
    required this.tcmDietaryAdvice, // 新增参数
  });
}

// 新增心理健康评估模型
@JsonSerializable()
class MentalHealthAssessment {
  final double stressLevel;
  final double sleepQuality;
  final List<String> copingStrategies;
  
  const MentalHealthAssessment({
    required this.stressLevel,
    required this.sleepQuality,
    required this.copingStrategies,
  });
}
