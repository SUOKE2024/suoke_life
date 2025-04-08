import 'dart:convert';
import 'constitution_type.dart';

/// 健康调理方案实体
///
/// 表示基于四诊数据和体质类型所制定的中医调理方案
class HealthRegimen {
  /// 调理方案ID
  final String id;
  
  /// 方案标题
  final String title;
  
  /// 方案描述
  final String description;
  
  /// 方案分类
  final String category;
  
  /// 方案标签
  final List<String> tags;
  
  /// 用户ID
  final String? userId;
  
  /// 方案创建时间
  final DateTime createdAt;
  
  /// 方案更新时间
  final DateTime updatedAt;
  
  /// 体质类型
  final ConstitutionType constitutionType;
  
  /// 诊断结论
  final String diagnosis;
  
  /// 诊断ID（关联四诊数据）
  final String? diagnosticDataId;
  
  /// 总体调理原则
  final String regimenPrinciple;
  
  /// 饮食调理建议
  final DietaryRegimen dietary;
  
  /// 情志调理建议
  final EmotionalRegimen emotional;
  
  /// 起居调理建议
  final LifestyleRegimen lifestyle;
  
  /// 运动调理建议
  final ExerciseRegimen exercise;
  
  /// 穴位保健建议
  final AcupointRegimen? acupoint;
  
  /// 中药调理建议
  final HerbalRegimen? herbal;
  
  /// 推荐食疗方
  final List<MedicinalDietItem>? medicinalDiet;
  
  /// 方案建议者ID
  final String? advisorId;
  
  /// 方案建议者名称
  final String? advisorName;
  
  /// 方案备注
  final String? notes;
  
  /// 附加建议
  final Map<String, dynamic>? additionalSuggestions;

  /// 创建健康调理方案实体
  const HealthRegimen({
    required this.id,
    required this.title,
    required this.description,
    required this.category,
    required this.tags,
    this.userId,
    required this.createdAt,
    required this.updatedAt,
    required this.constitutionType,
    required this.diagnosis,
    this.diagnosticDataId,
    required this.regimenPrinciple,
    required this.dietary,
    required this.emotional,
    required this.lifestyle,
    required this.exercise,
    this.acupoint,
    this.herbal,
    this.medicinalDiet,
    this.advisorId,
    this.advisorName,
    this.notes,
    this.additionalSuggestions,
  });
  
  /// 从JSON创建实例
  factory HealthRegimen.fromJson(Map<String, dynamic> json) {
    return HealthRegimen(
      id: json['id'] as String,
      title: json['title'] as String,
      description: json['description'] as String,
      category: json['category'] as String,
      tags: (json['tags'] as List).cast<String>(),
      userId: json['userId'] as String?,
      createdAt: DateTime.parse(json['createdAt'] as String),
      updatedAt: DateTime.parse(json['updatedAt'] as String),
      constitutionType: ConstitutionType.values.firstWhere(
        (type) => type.toString() == 'ConstitutionType.${json['constitutionType']}',
      ),
      diagnosis: json['diagnosis'] as String,
      diagnosticDataId: json['diagnosticDataId'] as String?,
      regimenPrinciple: json['regimenPrinciple'] as String,
      dietary: DietaryRegimen.fromJson(json['dietary'] as Map<String, dynamic>),
      emotional: EmotionalRegimen.fromJson(json['emotional'] as Map<String, dynamic>),
      lifestyle: LifestyleRegimen.fromJson(json['lifestyle'] as Map<String, dynamic>),
      exercise: ExerciseRegimen.fromJson(json['exercise'] as Map<String, dynamic>),
      acupoint: json['acupoint'] != null
          ? AcupointRegimen.fromJson(json['acupoint'] as Map<String, dynamic>)
          : null,
      herbal: json['herbal'] != null
          ? HerbalRegimen.fromJson(json['herbal'] as Map<String, dynamic>)
          : null,
      medicinalDiet: json['medicinalDiet'] != null
          ? (json['medicinalDiet'] as List)
              .map((e) => MedicinalDietItem.fromJson(e as Map<String, dynamic>))
              .toList()
          : null,
      advisorId: json['advisorId'] as String?,
      advisorName: json['advisorName'] as String?,
      notes: json['notes'] as String?,
      additionalSuggestions: json['additionalSuggestions'] as Map<String, dynamic>?,
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    final constitutionTypeString = constitutionType.toString().split('.').last;
    
    return {
      'id': id,
      'title': title,
      'description': description,
      'category': category,
      'tags': tags,
      if (userId != null) 'userId': userId,
      'createdAt': createdAt.toIso8601String(),
      'updatedAt': updatedAt.toIso8601String(),
      'constitutionType': constitutionTypeString,
      'diagnosis': diagnosis,
      if (diagnosticDataId != null) 'diagnosticDataId': diagnosticDataId,
      'regimenPrinciple': regimenPrinciple,
      'dietary': dietary.toJson(),
      'emotional': emotional.toJson(),
      'lifestyle': lifestyle.toJson(),
      'exercise': exercise.toJson(),
      if (acupoint != null) 'acupoint': acupoint!.toJson(),
      if (herbal != null) 'herbal': herbal!.toJson(),
      if (medicinalDiet != null)
        'medicinalDiet': medicinalDiet!.map((e) => e.toJson()).toList(),
      if (advisorId != null) 'advisorId': advisorId,
      if (advisorName != null) 'advisorName': advisorName,
      if (notes != null) 'notes': notes,
      if (additionalSuggestions != null) 'additionalSuggestions': additionalSuggestions,
    };
  }
  
  @override
  String toString() {
    return jsonEncode(toJson());
  }
}

/// 饮食调理建议
class DietaryRegimen {
  /// 饮食调理原则
  final String principle;
  
  /// 推荐食物
  final List<String> recommendedFoods;
  
  /// 限制食物
  final List<String> restrictedFoods;
  
  /// 禁忌食物
  final List<String> forbiddenFoods;
  
  /// 饮食特别建议
  final List<String> specialSuggestions;
  
  /// 饮食方法建议
  final String? methodSuggestions;
  
  /// 季节性饮食建议
  final Map<String, List<String>>? seasonalSuggestions;
  
  /// 创建饮食调理建议
  DietaryRegimen({
    required this.principle,
    required this.recommendedFoods,
    required this.restrictedFoods,
    required this.forbiddenFoods,
    required this.specialSuggestions,
    this.methodSuggestions,
    this.seasonalSuggestions,
  });
  
  /// 从JSON创建实例
  factory DietaryRegimen.fromJson(Map<String, dynamic> json) {
    return DietaryRegimen(
      principle: json['principle'] as String,
      recommendedFoods: (json['recommendedFoods'] as List).cast<String>(),
      restrictedFoods: (json['restrictedFoods'] as List).cast<String>(),
      forbiddenFoods: (json['forbiddenFoods'] as List).cast<String>(),
      specialSuggestions: (json['specialSuggestions'] as List).cast<String>(),
      methodSuggestions: json['methodSuggestions'] as String?,
      seasonalSuggestions: json['seasonalSuggestions'] != null
          ? (json['seasonalSuggestions'] as Map).map(
              (k, v) => MapEntry(k.toString(), (v as List).cast<String>()),
            )
          : null,
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'principle': principle,
      'recommendedFoods': recommendedFoods,
      'restrictedFoods': restrictedFoods,
      'forbiddenFoods': forbiddenFoods,
      'specialSuggestions': specialSuggestions,
      if (methodSuggestions != null) 'methodSuggestions': methodSuggestions,
      if (seasonalSuggestions != null) 'seasonalSuggestions': seasonalSuggestions,
    };
  }
}

/// 情志调理建议
class EmotionalRegimen {
  /// 情志调理原则
  final String principle;
  
  /// 情绪风险
  final List<String> emotionalRisks;
  
  /// 情绪调理建议
  final List<String> suggestions;
  
  /// 心理疗法建议
  final List<String>? therapySuggestions;
  
  /// 其他情志调理建议
  final Map<String, dynamic>? additionalSuggestions;
  
  /// 创建情志调理建议
  EmotionalRegimen({
    required this.principle,
    required this.emotionalRisks,
    required this.suggestions,
    this.therapySuggestions,
    this.additionalSuggestions,
  });
  
  /// 从JSON创建实例
  factory EmotionalRegimen.fromJson(Map<String, dynamic> json) {
    return EmotionalRegimen(
      principle: json['principle'] as String,
      emotionalRisks: (json['emotionalRisks'] as List).cast<String>(),
      suggestions: (json['suggestions'] as List).cast<String>(),
      therapySuggestions: (json['therapySuggestions'] as List?)?.cast<String>(),
      additionalSuggestions: json['additionalSuggestions'] as Map<String, dynamic>?,
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'principle': principle,
      'emotionalRisks': emotionalRisks,
      'suggestions': suggestions,
      if (therapySuggestions != null) 'therapySuggestions': therapySuggestions,
      if (additionalSuggestions != null) 'additionalSuggestions': additionalSuggestions,
    };
  }
}

/// 起居调理建议
class LifestyleRegimen {
  /// 起居调理原则
  final String principle;
  
  /// 作息时间建议
  final String schedule;
  
  /// 睡眠建议
  final List<String> sleepSuggestions;
  
  /// 环境建议
  final List<String> environmentSuggestions;
  
  /// 洗浴、保健建议
  final List<String> hygieneSuggestions;
  
  /// 季节调理建议
  final Map<String, List<String>>? seasonalSuggestions;
  
  /// 其他起居建议
  final Map<String, dynamic>? additionalSuggestions;
  
  /// 创建起居调理建议
  LifestyleRegimen({
    required this.principle,
    required this.schedule,
    required this.sleepSuggestions,
    required this.environmentSuggestions,
    required this.hygieneSuggestions,
    this.seasonalSuggestions,
    this.additionalSuggestions,
  });
  
  /// 从JSON创建实例
  factory LifestyleRegimen.fromJson(Map<String, dynamic> json) {
    return LifestyleRegimen(
      principle: json['principle'] as String,
      schedule: json['schedule'] as String,
      sleepSuggestions: (json['sleepSuggestions'] as List).cast<String>(),
      environmentSuggestions: (json['environmentSuggestions'] as List).cast<String>(),
      hygieneSuggestions: (json['hygieneSuggestions'] as List).cast<String>(),
      seasonalSuggestions: json['seasonalSuggestions'] != null
          ? (json['seasonalSuggestions'] as Map).map(
              (k, v) => MapEntry(k.toString(), (v as List).cast<String>()),
            )
          : null,
      additionalSuggestions: json['additionalSuggestions'] as Map<String, dynamic>?,
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'principle': principle,
      'schedule': schedule,
      'sleepSuggestions': sleepSuggestions,
      'environmentSuggestions': environmentSuggestions,
      'hygieneSuggestions': hygieneSuggestions,
      if (seasonalSuggestions != null) 'seasonalSuggestions': seasonalSuggestions,
      if (additionalSuggestions != null) 'additionalSuggestions': additionalSuggestions,
    };
  }
}

/// 运动调理建议
class ExerciseRegimen {
  /// 运动调理原则
  final String principle;
  
  /// 推荐运动方式
  final List<String> recommendedExercises;
  
  /// 运动强度
  final String intensity;
  
  /// 运动频率
  final String frequency;
  
  /// 运动禁忌
  final List<String> contraindications;
  
  /// 传统养生功法建议
  final List<TraditionalExercise>? traditionalExercises;
  
  /// 其他运动建议
  final Map<String, dynamic>? additionalSuggestions;
  
  /// 创建运动调理建议
  ExerciseRegimen({
    required this.principle,
    required this.recommendedExercises,
    required this.intensity,
    required this.frequency,
    required this.contraindications,
    this.traditionalExercises,
    this.additionalSuggestions,
  });
  
  /// 从JSON创建实例
  factory ExerciseRegimen.fromJson(Map<String, dynamic> json) {
    return ExerciseRegimen(
      principle: json['principle'] as String,
      recommendedExercises: (json['recommendedExercises'] as List).cast<String>(),
      intensity: json['intensity'] as String,
      frequency: json['frequency'] as String,
      contraindications: (json['contraindications'] as List).cast<String>(),
      traditionalExercises: json['traditionalExercises'] != null
          ? (json['traditionalExercises'] as List)
              .map((e) => TraditionalExercise.fromJson(e as Map<String, dynamic>))
              .toList()
          : null,
      additionalSuggestions: json['additionalSuggestions'] as Map<String, dynamic>?,
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'principle': principle,
      'recommendedExercises': recommendedExercises,
      'intensity': intensity,
      'frequency': frequency,
      'contraindications': contraindications,
      if (traditionalExercises != null)
        'traditionalExercises': traditionalExercises!.map((e) => e.toJson()).toList(),
      if (additionalSuggestions != null) 'additionalSuggestions': additionalSuggestions,
    };
  }
}

/// 传统养生功法
class TraditionalExercise {
  /// 功法名称
  final String name;
  
  /// 功法类型（如太极拳、八段锦、五禽戏等）
  final String type;
  
  /// 功法特点
  final String characteristics;
  
  /// 功法描述
  final String description;
  
  /// 功法指导（步骤说明）
  final List<String> instructions;
  
  /// 效果与功效
  final List<String> benefits;
  
  /// 视频教程链接
  final String? videoUrl;
  
  /// 图片指导链接
  final List<String>? imageUrls;
  
  /// 创建传统养生功法
  TraditionalExercise({
    required this.name,
    required this.type,
    required this.characteristics,
    required this.description,
    required this.instructions,
    required this.benefits,
    this.videoUrl,
    this.imageUrls,
  });
  
  /// 从JSON创建实例
  factory TraditionalExercise.fromJson(Map<String, dynamic> json) {
    return TraditionalExercise(
      name: json['name'] as String,
      type: json['type'] as String,
      characteristics: json['characteristics'] as String,
      description: json['description'] as String,
      instructions: (json['instructions'] as List).cast<String>(),
      benefits: (json['benefits'] as List).cast<String>(),
      videoUrl: json['videoUrl'] as String?,
      imageUrls: (json['imageUrls'] as List?)?.cast<String>(),
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'type': type,
      'characteristics': characteristics,
      'description': description,
      'instructions': instructions,
      'benefits': benefits,
      if (videoUrl != null) 'videoUrl': videoUrl,
      if (imageUrls != null) 'imageUrls': imageUrls,
    };
  }
}

/// 穴位保健调理建议
class AcupointRegimen {
  /// 穴位调理原则
  final String principle;
  
  /// 推荐穴位
  final List<AcupointRecommendation> recommendations;
  
  /// 穴位按摩方法
  final List<String> massageMethods;
  
  /// 穴位疗法建议
  final List<String>? therapySuggestions;
  
  /// 禁忌
  final List<String> contraindications;
  
  /// 穴位保健方案图示链接
  final List<String>? imageUrls;
  
  /// 创建穴位保健调理建议
  AcupointRegimen({
    required this.principle,
    required this.recommendations,
    required this.massageMethods,
    this.therapySuggestions,
    required this.contraindications,
    this.imageUrls,
  });
  
  /// 从JSON创建实例
  factory AcupointRegimen.fromJson(Map<String, dynamic> json) {
    return AcupointRegimen(
      principle: json['principle'] as String,
      recommendations: (json['recommendations'] as List)
          .map((e) => AcupointRecommendation.fromJson(e as Map<String, dynamic>))
          .toList(),
      massageMethods: (json['massageMethods'] as List).cast<String>(),
      therapySuggestions: (json['therapySuggestions'] as List?)?.cast<String>(),
      contraindications: (json['contraindications'] as List).cast<String>(),
      imageUrls: (json['imageUrls'] as List?)?.cast<String>(),
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'principle': principle,
      'recommendations': recommendations.map((e) => e.toJson()).toList(),
      'massageMethods': massageMethods,
      if (therapySuggestions != null) 'therapySuggestions': therapySuggestions,
      'contraindications': contraindications,
      if (imageUrls != null) 'imageUrls': imageUrls,
    };
  }
}

/// 穴位推荐
class AcupointRecommendation {
  /// 穴位名称
  final String name;
  
  /// 穴位位置
  final String location;
  
  /// 穴位功效
  final List<String> benefits;
  
  /// 按摩方法
  final String method;
  
  /// 频率
  final String frequency;
  
  /// 特别说明
  final String? specialNotes;
  
  /// 创建穴位推荐
  AcupointRecommendation({
    required this.name,
    required this.location,
    required this.benefits,
    required this.method,
    required this.frequency,
    this.specialNotes,
  });
  
  /// 从JSON创建实例
  factory AcupointRecommendation.fromJson(Map<String, dynamic> json) {
    return AcupointRecommendation(
      name: json['name'] as String,
      location: json['location'] as String,
      benefits: (json['benefits'] as List).cast<String>(),
      method: json['method'] as String,
      frequency: json['frequency'] as String,
      specialNotes: json['specialNotes'] as String?,
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'location': location,
      'benefits': benefits,
      'method': method,
      'frequency': frequency,
      if (specialNotes != null) 'specialNotes': specialNotes,
    };
  }
}

/// 中药调理建议
class HerbalRegimen {
  /// 中药调理原则
  final String principle;
  
  /// 推荐中药方剂
  final List<HerbalFormula> formulas;
  
  /// 中药配伍禁忌
  final List<String> incompatibilities;
  
  /// 服药注意事项
  final List<String> precautions;
  
  /// 中药调理周期
  final String treatmentCycle;
  
  /// 其他中药调理建议
  final Map<String, dynamic>? additionalSuggestions;
  
  /// 创建中药调理建议
  HerbalRegimen({
    required this.principle,
    required this.formulas,
    required this.incompatibilities,
    required this.precautions,
    required this.treatmentCycle,
    this.additionalSuggestions,
  });
  
  /// 从JSON创建实例
  factory HerbalRegimen.fromJson(Map<String, dynamic> json) {
    return HerbalRegimen(
      principle: json['principle'] as String,
      formulas: (json['formulas'] as List)
          .map((e) => HerbalFormula.fromJson(e as Map<String, dynamic>))
          .toList(),
      incompatibilities: (json['incompatibilities'] as List).cast<String>(),
      precautions: (json['precautions'] as List).cast<String>(),
      treatmentCycle: json['treatmentCycle'] as String,
      additionalSuggestions: json['additionalSuggestions'] as Map<String, dynamic>?,
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'principle': principle,
      'formulas': formulas.map((e) => e.toJson()).toList(),
      'incompatibilities': incompatibilities,
      'precautions': precautions,
      'treatmentCycle': treatmentCycle,
      if (additionalSuggestions != null) 'additionalSuggestions': additionalSuggestions,
    };
  }
}

/// 中药方剂
class HerbalFormula {
  /// 方剂名称
  final String name;
  
  /// 方剂组成
  final List<HerbalIngredient> ingredients;
  
  /// 功效
  final List<String> effects;
  
  /// 主治
  final List<String> indications;
  
  /// 用法用量
  final String dosageInstructions;
  
  /// 禁忌
  final List<String> contraindications;
  
  /// 方剂来源
  final String? source;
  
  /// 现代研究
  final String? modernResearch;
  
  /// 创建中药方剂
  HerbalFormula({
    required this.name,
    required this.ingredients,
    required this.effects,
    required this.indications,
    required this.dosageInstructions,
    required this.contraindications,
    this.source,
    this.modernResearch,
  });
  
  /// 从JSON创建实例
  factory HerbalFormula.fromJson(Map<String, dynamic> json) {
    return HerbalFormula(
      name: json['name'] as String,
      ingredients: (json['ingredients'] as List)
          .map((e) => HerbalIngredient.fromJson(e as Map<String, dynamic>))
          .toList(),
      effects: (json['effects'] as List).cast<String>(),
      indications: (json['indications'] as List).cast<String>(),
      dosageInstructions: json['dosageInstructions'] as String,
      contraindications: (json['contraindications'] as List).cast<String>(),
      source: json['source'] as String?,
      modernResearch: json['modernResearch'] as String?,
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'ingredients': ingredients.map((e) => e.toJson()).toList(),
      'effects': effects,
      'indications': indications,
      'dosageInstructions': dosageInstructions,
      'contraindications': contraindications,
      if (source != null) 'source': source,
      if (modernResearch != null) 'modernResearch': modernResearch,
    };
  }
}

/// 中药材
class HerbalIngredient {
  /// 药材名称
  final String name;
  
  /// 用量
  final String dosage;
  
  /// 药材功效
  final List<String>? effects;
  
  /// 炮制方法
  final String? processingMethod;
  
  /// 创建中药材
  HerbalIngredient({
    required this.name,
    required this.dosage,
    this.effects,
    this.processingMethod,
  });
  
  /// 从JSON创建实例
  factory HerbalIngredient.fromJson(Map<String, dynamic> json) {
    return HerbalIngredient(
      name: json['name'] as String,
      dosage: json['dosage'] as String,
      effects: (json['effects'] as List?)?.cast<String>(),
      processingMethod: json['processingMethod'] as String?,
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'dosage': dosage,
      if (effects != null) 'effects': effects,
      if (processingMethod != null) 'processingMethod': processingMethod,
    };
  }
}

/// 食疗方
class MedicinalDietItem {
  /// 食疗方名称
  final String name;
  
  /// 食疗方组成
  final List<DietIngredient> ingredients;
  
  /// 制作方法
  final List<String> preparationSteps;
  
  /// 功效
  final List<String> benefits;
  
  /// 适用体质
  final List<ConstitutionType> suitableConstitutions;
  
  /// 禁忌
  final List<String> contraindications;
  
  /// 食用方法
  final String consumptionMethod;
  
  /// 创建食疗方
  MedicinalDietItem({
    required this.name,
    required this.ingredients,
    required this.preparationSteps,
    required this.benefits,
    required this.suitableConstitutions,
    required this.contraindications,
    required this.consumptionMethod,
  });
  
  /// 从JSON创建实例
  factory MedicinalDietItem.fromJson(Map<String, dynamic> json) {
    return MedicinalDietItem(
      name: json['name'] as String,
      ingredients: (json['ingredients'] as List)
          .map((e) => DietIngredient.fromJson(e as Map<String, dynamic>))
          .toList(),
      preparationSteps: (json['preparationSteps'] as List).cast<String>(),
      benefits: (json['benefits'] as List).cast<String>(),
      suitableConstitutions: (json['suitableConstitutions'] as List).map((e) => 
          ConstitutionType.values.firstWhere(
            (type) => type.toString() == 'ConstitutionType.$e',
          )
      ).toList(),
      contraindications: (json['contraindications'] as List).cast<String>(),
      consumptionMethod: json['consumptionMethod'] as String,
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'ingredients': ingredients.map((e) => e.toJson()).toList(),
      'preparationSteps': preparationSteps,
      'benefits': benefits,
      'suitableConstitutions': suitableConstitutions
          .map((e) => e.toString().split('.').last)
          .toList(),
      'contraindications': contraindications,
      'consumptionMethod': consumptionMethod,
    };
  }
}

/// 食疗材料
class DietIngredient {
  /// 材料名称
  final String name;
  
  /// 用量
  final String amount;
  
  /// 材料功效
  final List<String>? effects;
  
  /// 处理方法
  final String? processingMethod;
  
  /// 创建食疗材料
  DietIngredient({
    required this.name,
    required this.amount,
    this.effects,
    this.processingMethod,
  });
  
  /// 从JSON创建实例
  factory DietIngredient.fromJson(Map<String, dynamic> json) {
    return DietIngredient(
      name: json['name'] as String,
      amount: json['amount'] as String,
      effects: (json['effects'] as List?)?.cast<String>(),
      processingMethod: json['processingMethod'] as String?,
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'amount': amount,
      if (effects != null) 'effects': effects,
      if (processingMethod != null) 'processingMethod': processingMethod,
    };
  }
} 