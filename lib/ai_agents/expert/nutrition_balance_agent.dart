import 'dart:async';
import 'dart:math';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../core/agent_microkernel.dart';
import '../models/ai_agent.dart';
import '../core/autonomous_learning_system.dart';
import '../core/security_privacy_framework.dart';
import '../rag/rag_service.dart';
import '../supply_chain/medicinal_food_agent.dart';
import '../../core/utils/logger.dart';
import 'health_management_agent.dart';
import 'knowledge_graph_agent.dart';

/// 宏量营养素类型
enum MacronutrientType {
  /// 蛋白质
  protein,
  
  /// 碳水化合物
  carbohydrate,
  
  /// 脂肪
  fat,
  
  /// 纤维素
  fiber,
}

/// 微量营养素类型
enum MicronutrientType {
  /// 维生素A
  vitaminA,
  
  /// 维生素B群
  vitaminB,
  
  /// 维生素C
  vitaminC,
  
  /// 维生素D
  vitaminD,
  
  /// 维生素E
  vitaminE,
  
  /// 维生素K
  vitaminK,
  
  /// 钙
  calcium,
  
  /// 铁
  iron,
  
  /// 锌
  zinc,
  
  /// 镁
  magnesium,
  
  /// 钾
  potassium,
  
  /// 硒
  selenium,
  
  /// 铬
  chromium,
  
  /// 碘
  iodine,
}

/// 饮食类型
enum DietType {
  /// 普通饮食
  regular,
  
  /// 素食
  vegetarian,
  
  /// 纯素食
  vegan,
  
  /// 低碳水化合物
  lowCarb,
  
  /// 生酮饮食
  keto,
  
  /// 间歇性断食
  intermittentFasting,
  
  /// 地中海饮食
  mediterranean,
  
  /// 无麸质饮食
  glutenFree,
  
  /// 无乳糖饮食
  lactoseFree,
  
  /// 高蛋白饮食
  highProtein,
  
  /// 低脂饮食
  lowFat,
  
  /// 中医食疗
  tcmDiet,
}

/// 膳食计划类型
enum MealPlanType {
  /// 减重
  weightLoss,
  
  /// 增肌
  muscleGain,
  
  /// 维持健康
  maintenance,
  
  /// 疾病预防
  diseasePrevention,
  
  /// 能量补充
  energyBoost,
  
  /// 提高免疫力
  immunityBoost,
  
  /// 改善消化
  digestiveHealth,
  
  /// 改善睡眠
  sleepImprovement,
  
  /// 心脏健康
  heartHealth,
  
  /// 脑健康
  brainHealth,
  
  /// 孕期营养
  pregnancy,
  
  /// 老年保健
  elderCare,
  
  /// 儿童成长
  childDevelopment,
}

/// 营养素摄入量
class NutrientIntake {
  /// 营养素名称
  final String name;
  
  /// 摄入量
  final double amount;
  
  /// 计量单位
  final String unit;
  
  /// 推荐摄入量
  final double recommendedAmount;
  
  /// 上限
  final double? upperLimit;
  
  NutrientIntake({
    required this.name,
    required this.amount,
    required this.unit,
    required this.recommendedAmount,
    this.upperLimit,
  });
  
  /// 计算摄入状态
  NutrientIntakeStatus get status {
    final percentage = amount / recommendedAmount * 100;
    
    if (percentage < 70) {
      return NutrientIntakeStatus.deficient;
    } else if (percentage >= 70 && percentage < 90) {
      return NutrientIntakeStatus.suboptimal;
    } else if (percentage >= 90 && percentage <= 110) {
      return NutrientIntakeStatus.optimal;
    } else if (upperLimit != null && amount > upperLimit!) {
      return NutrientIntakeStatus.excessive;
    } else {
      return NutrientIntakeStatus.aboveOptimal;
    }
  }
  
  /// 转换为Map
  Map<String, dynamic> toMap() {
    return {
      'name': name,
      'amount': amount,
      'unit': unit,
      'recommendedAmount': recommendedAmount,
      'upperLimit': upperLimit,
      'status': status.toString().split('.').last,
    };
  }
  
  /// 从Map创建
  factory NutrientIntake.fromMap(Map<String, dynamic> map) {
    return NutrientIntake(
      name: map['name'],
      amount: map['amount'],
      unit: map['unit'],
      recommendedAmount: map['recommendedAmount'],
      upperLimit: map['upperLimit'],
    );
  }
}

/// 营养素摄入状态
enum NutrientIntakeStatus {
  /// 缺乏
  deficient,
  
  /// 不足
  suboptimal,
  
  /// 最佳
  optimal,
  
  /// 高于最佳
  aboveOptimal,
  
  /// 过量
  excessive,
}

/// 食物记录
class FoodRecord {
  /// 记录ID
  final String id;
  
  /// 食物名称
  final String name;
  
  /// 食物分类
  final String category;
  
  /// 摄入量
  final double amount;
  
  /// 单位
  final String unit;
  
  /// 热量（千卡）
  final double calories;
  
  /// 蛋白质（克）
  final double protein;
  
  /// 碳水化合物（克）
  final double carbohydrates;
  
  /// 脂肪（克）
  final double fat;
  
  /// 纤维素（克）
  final double? fiber;
  
  /// 糖分（克）
  final double? sugar;
  
  /// 维生素和矿物质含量
  final Map<String, double>? micronutrients;
  
  /// 记录时间
  final DateTime timestamp;
  
  /// 餐次
  final String? mealType;
  
  /// 用户ID
  final String userId;
  
  /// 相关的中医食疗属性
  final List<TCMFoodProperty>? tcmProperties;
  
  FoodRecord({
    required this.id,
    required this.name,
    required this.category,
    required this.amount,
    required this.unit,
    required this.calories,
    required this.protein,
    required this.carbohydrates,
    required this.fat,
    this.fiber,
    this.sugar,
    this.micronutrients,
    required this.timestamp,
    this.mealType,
    required this.userId,
    this.tcmProperties,
  });
  
  /// 转换为Map
  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'name': name,
      'category': category,
      'amount': amount,
      'unit': unit,
      'calories': calories,
      'protein': protein,
      'carbohydrates': carbohydrates,
      'fat': fat,
      'fiber': fiber,
      'sugar': sugar,
      'micronutrients': micronutrients,
      'timestamp': timestamp.toIso8601String(),
      'mealType': mealType,
      'userId': userId,
      'tcmProperties': tcmProperties?.map((p) => p.toString().split('.').last).toList(),
    };
  }
  
  /// 从Map创建
  factory FoodRecord.fromMap(Map<String, dynamic> map) {
    return FoodRecord(
      id: map['id'],
      name: map['name'],
      category: map['category'],
      amount: map['amount'],
      unit: map['unit'],
      calories: map['calories'],
      protein: map['protein'],
      carbohydrates: map['carbohydrates'],
      fat: map['fat'],
      fiber: map['fiber'],
      sugar: map['sugar'],
      micronutrients: map['micronutrients'] != null 
          ? Map<String, double>.from(map['micronutrients']) 
          : null,
      timestamp: DateTime.parse(map['timestamp']),
      mealType: map['mealType'],
      userId: map['userId'],
      tcmProperties: map['tcmProperties'] != null 
          ? (map['tcmProperties'] as List)
              .map((p) => TCMFoodProperty.values.firstWhere(
                  (v) => v.toString().split('.').last == p))
              .toList() 
          : null,
    );
  }
}

/// 营养摄入摘要
class NutritionSummary {
  /// 总热量（千卡）
  final double totalCalories;
  
  /// 蛋白质总量（克）
  final double totalProtein;
  
  /// 碳水化合物总量（克）
  final double totalCarbohydrates;
  
  /// 脂肪总量（克）
  final double totalFat;
  
  /// 纤维素总量（克）
  final double totalFiber;
  
  /// 营养素摄入情况
  final List<NutrientIntake> nutrientIntakes;
  
  /// 开始日期
  final DateTime startDate;
  
  /// 结束日期
  final DateTime endDate;
  
  /// 用户ID
  final String userId;
  
  /// 评分（0-100）
  final double? nutritionScore;
  
  /// 存在的营养不平衡问题
  final List<String>? nutritionalImbalances;
  
  /// 改善建议
  final List<String>? improvementSuggestions;
  
  NutritionSummary({
    required this.totalCalories,
    required this.totalProtein,
    required this.totalCarbohydrates,
    required this.totalFat,
    required this.totalFiber,
    required this.nutrientIntakes,
    required this.startDate,
    required this.endDate,
    required this.userId,
    this.nutritionScore,
    this.nutritionalImbalances,
    this.improvementSuggestions,
  });
  
  /// 转换为Map
  Map<String, dynamic> toMap() {
    return {
      'totalCalories': totalCalories,
      'totalProtein': totalProtein,
      'totalCarbohydrates': totalCarbohydrates,
      'totalFat': totalFat,
      'totalFiber': totalFiber,
      'nutrientIntakes': nutrientIntakes.map((n) => n.toMap()).toList(),
      'startDate': startDate.toIso8601String(),
      'endDate': endDate.toIso8601String(),
      'userId': userId,
      'nutritionScore': nutritionScore,
      'nutritionalImbalances': nutritionalImbalances,
      'improvementSuggestions': improvementSuggestions,
    };
  }
  
  /// 从Map创建
  factory NutritionSummary.fromMap(Map<String, dynamic> map) {
    return NutritionSummary(
      totalCalories: map['totalCalories'],
      totalProtein: map['totalProtein'],
      totalCarbohydrates: map['totalCarbohydrates'],
      totalFat: map['totalFat'],
      totalFiber: map['totalFiber'],
      nutrientIntakes: (map['nutrientIntakes'] as List)
          .map((n) => NutrientIntake.fromMap(n))
          .toList(),
      startDate: DateTime.parse(map['startDate']),
      endDate: DateTime.parse(map['endDate']),
      userId: map['userId'],
      nutritionScore: map['nutritionScore'],
      nutritionalImbalances: map['nutritionalImbalances'] != null 
          ? List<String>.from(map['nutritionalImbalances']) 
          : null,
      improvementSuggestions: map['improvementSuggestions'] != null 
          ? List<String>.from(map['improvementSuggestions']) 
          : null,
    );
  }
}

/// 膳食计划
class MealPlan {
  /// 计划ID
  final String id;
  
  /// 用户ID
  final String userId;
  
  /// 计划名称
  final String name;
  
  /// 计划类型
  final MealPlanType type;
  
  /// 饮食类型
  final DietType dietType;
  
  /// 总热量目标（每日/千卡）
  final double targetCalories;
  
  /// 蛋白质目标（每日/克）
  final double targetProtein;
  
  /// 碳水化合物目标（每日/克）
  final double targetCarbohydrates;
  
  /// 脂肪目标（每日/克）
  final double targetFat;
  
  /// 开始日期
  final DateTime startDate;
  
  /// 结束日期
  final DateTime endDate;
  
  /// 每日膳食安排
  final List<DailyMealSchedule> mealSchedules;
  
  /// 注意事项
  final List<String>? notes;
  
  /// 个性化建议
  final List<String>? personalizedRecommendations;
  
  /// 体重目标（如果适用）
  final double? weightGoal;
  
  /// 健康目标
  final List<String>? healthGoals;
  
  /// 相关健康状况
  final List<String>? healthConditions;
  
  /// 根据体质推荐
  final TraditionalChineseBodyType? bodyType;
  
  MealPlan({
    required this.id,
    required this.userId,
    required this.name,
    required this.type,
    required this.dietType,
    required this.targetCalories,
    required this.targetProtein,
    required this.targetCarbohydrates,
    required this.targetFat,
    required this.startDate,
    required this.endDate,
    required this.mealSchedules,
    this.notes,
    this.personalizedRecommendations,
    this.weightGoal,
    this.healthGoals,
    this.healthConditions,
    this.bodyType,
  });
  
  /// 转换为Map
  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'userId': userId,
      'name': name,
      'type': type.toString().split('.').last,
      'dietType': dietType.toString().split('.').last,
      'targetCalories': targetCalories,
      'targetProtein': targetProtein,
      'targetCarbohydrates': targetCarbohydrates,
      'targetFat': targetFat,
      'startDate': startDate.toIso8601String(),
      'endDate': endDate.toIso8601String(),
      'mealSchedules': mealSchedules.map((m) => m.toMap()).toList(),
      'notes': notes,
      'personalizedRecommendations': personalizedRecommendations,
      'weightGoal': weightGoal,
      'healthGoals': healthGoals,
      'healthConditions': healthConditions,
      'bodyType': bodyType?.toString().split('.').last,
    };
  }
  
  /// 从Map创建
  factory MealPlan.fromMap(Map<String, dynamic> map) {
    return MealPlan(
      id: map['id'],
      userId: map['userId'],
      name: map['name'],
      type: MealPlanType.values.firstWhere(
          (e) => e.toString().split('.').last == map['type']),
      dietType: DietType.values.firstWhere(
          (e) => e.toString().split('.').last == map['dietType']),
      targetCalories: map['targetCalories'],
      targetProtein: map['targetProtein'],
      targetCarbohydrates: map['targetCarbohydrates'],
      targetFat: map['targetFat'],
      startDate: DateTime.parse(map['startDate']),
      endDate: DateTime.parse(map['endDate']),
      mealSchedules: (map['mealSchedules'] as List)
          .map((m) => DailyMealSchedule.fromMap(m))
          .toList(),
      notes: map['notes'] != null ? List<String>.from(map['notes']) : null,
      personalizedRecommendations: map['personalizedRecommendations'] != null 
          ? List<String>.from(map['personalizedRecommendations']) 
          : null,
      weightGoal: map['weightGoal'],
      healthGoals: map['healthGoals'] != null 
          ? List<String>.from(map['healthGoals']) 
          : null,
      healthConditions: map['healthConditions'] != null 
          ? List<String>.from(map['healthConditions']) 
          : null,
      bodyType: map['bodyType'] != null 
          ? TraditionalChineseBodyType.values.firstWhere(
              (e) => e.toString().split('.').last == map['bodyType']) 
          : null,
    );
  }
}

/// 每日膳食安排
class DailyMealSchedule {
  /// 日期
  final DateTime date;
  
  /// 膳食列表
  final List<Meal> meals;
  
  /// 总热量
  final double totalCalories;
  
  /// 总蛋白质
  final double totalProtein;
  
  /// 总碳水化合物
  final double totalCarbohydrates;
  
  /// 总脂肪
  final double totalFat;
  
  /// 特殊说明
  final String? specialInstructions;
  
  /// 季节性调整
  final String? seasonalAdjustment;
  
  DailyMealSchedule({
    required this.date,
    required this.meals,
    required this.totalCalories,
    required this.totalProtein,
    required this.totalCarbohydrates,
    required this.totalFat,
    this.specialInstructions,
    this.seasonalAdjustment,
  });
  
  /// 转换为Map
  Map<String, dynamic> toMap() {
    return {
      'date': date.toIso8601String(),
      'meals': meals.map((m) => m.toMap()).toList(),
      'totalCalories': totalCalories,
      'totalProtein': totalProtein,
      'totalCarbohydrates': totalCarbohydrates,
      'totalFat': totalFat,
      'specialInstructions': specialInstructions,
      'seasonalAdjustment': seasonalAdjustment,
    };
  }
  
  /// 从Map创建
  factory DailyMealSchedule.fromMap(Map<String, dynamic> map) {
    return DailyMealSchedule(
      date: DateTime.parse(map['date']),
      meals: (map['meals'] as List).map((m) => Meal.fromMap(m)).toList(),
      totalCalories: map['totalCalories'],
      totalProtein: map['totalProtein'],
      totalCarbohydrates: map['totalCarbohydrates'],
      totalFat: map['totalFat'],
      specialInstructions: map['specialInstructions'],
      seasonalAdjustment: map['seasonalAdjustment'],
    );
  }
}

/// 膳食
class Meal {
  /// 膳食ID
  final String id;
  
  /// 名称
  final String name;
  
  /// 类型（早餐、午餐、晚餐等）
  final String type;
  
  /// 时间
  final TimeOfDay timeOfDay;
  
  /// 食物列表
  final List<MealFoodItem> foodItems;
  
  /// 总热量
  final double totalCalories;
  
  /// 总蛋白质
  final double totalProtein;
  
  /// 总碳水化合物
  final double totalCarbohydrates;
  
  /// 总脂肪
  final double totalFat;
  
  /// 准备说明
  final String? preparationInstructions;
  
  /// 食疗效果
  final List<FoodTherapeuticEffect>? therapeuticEffects;
  
  Meal({
    required this.id,
    required this.name,
    required this.type,
    required this.timeOfDay,
    required this.foodItems,
    required this.totalCalories,
    required this.totalProtein,
    required this.totalCarbohydrates,
    required this.totalFat,
    this.preparationInstructions,
    this.therapeuticEffects,
  });
  
  /// 转换为Map
  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'name': name,
      'type': type,
      'timeOfDay': '${timeOfDay.hour}:${timeOfDay.minute}',
      'foodItems': foodItems.map((f) => f.toMap()).toList(),
      'totalCalories': totalCalories,
      'totalProtein': totalProtein,
      'totalCarbohydrates': totalCarbohydrates,
      'totalFat': totalFat,
      'preparationInstructions': preparationInstructions,
      'therapeuticEffects': therapeuticEffects?.map((e) => e.toString().split('.').last).toList(),
    };
  }
  
  /// 从Map创建
  factory Meal.fromMap(Map<String, dynamic> map) {
    final timeParts = (map['timeOfDay'] as String).split(':');
    return Meal(
      id: map['id'],
      name: map['name'],
      type: map['type'],
      timeOfDay: TimeOfDay(
        hour: int.parse(timeParts[0]), 
        minute: int.parse(timeParts[1]),
      ),
      foodItems: (map['foodItems'] as List)
          .map((f) => MealFoodItem.fromMap(f))
          .toList(),
      totalCalories: map['totalCalories'],
      totalProtein: map['totalProtein'],
      totalCarbohydrates: map['totalCarbohydrates'],
      totalFat: map['totalFat'],
      preparationInstructions: map['preparationInstructions'],
      therapeuticEffects: map['therapeuticEffects'] != null 
          ? (map['therapeuticEffects'] as List)
              .map((e) => FoodTherapeuticEffect.values.firstWhere(
                  (v) => v.toString().split('.').last == e))
              .toList() 
          : null,
    );
  }
}

/// 膳食中的食物项
class MealFoodItem {
  /// 食物名称
  final String name;
  
  /// 数量
  final double amount;
  
  /// 单位
  final String unit;
  
  /// 热量
  final double calories;
  
  /// 蛋白质
  final double protein;
  
  /// 碳水化合物
  final double carbohydrates;
  
  /// 脂肪
  final double fat;
  
  /// 相关的食物ID
  final String? foodId;
  
  /// 替代选项
  final List<String>? alternatives;
  
  /// 准备方法
  final String? preparationMethod;
  
  /// 中医属性
  final List<TCMFoodProperty>? tcmProperties;
  
  MealFoodItem({
    required this.name,
    required this.amount,
    required this.unit,
    required this.calories,
    required this.protein,
    required this.carbohydrates,
    required this.fat,
    this.foodId,
    this.alternatives,
    this.preparationMethod,
    this.tcmProperties,
  });
  
  /// 转换为Map
  Map<String, dynamic> toMap() {
    return {
      'name': name,
      'amount': amount,
      'unit': unit,
      'calories': calories,
      'protein': protein,
      'carbohydrates': carbohydrates,
      'fat': fat,
      'foodId': foodId,
      'alternatives': alternatives,
      'preparationMethod': preparationMethod,
      'tcmProperties': tcmProperties?.map((p) => p.toString().split('.').last).toList(),
    };
  }
  
  /// 从Map创建
  factory MealFoodItem.fromMap(Map<String, dynamic> map) {
    return MealFoodItem(
      name: map['name'],
      amount: map['amount'],
      unit: map['unit'],
      calories: map['calories'],
      protein: map['protein'],
      carbohydrates: map['carbohydrates'],
      fat: map['fat'],
      foodId: map['foodId'],
      alternatives: map['alternatives'] != null 
          ? List<String>.from(map['alternatives']) 
          : null,
      preparationMethod: map['preparationMethod'],
      tcmProperties: map['tcmProperties'] != null 
          ? (map['tcmProperties'] as List)
              .map((p) => TCMFoodProperty.values.firstWhere(
                  (v) => v.toString().split('.').last == p))
              .toList() 
          : null,
    );
  }
}

/// 营养素数据库
class NutrientDatabase {
  /// 食物名称
  final String name;
  
  /// 每100克/毫升的营养数据
  final Map<String, double> nutrientsPerServing;
  
  /// 服务尺寸（克/毫升）
  final double servingSize;
  
  /// 服务单位
  final String servingUnit;
  
  /// 食物类别
  final String category;
  
  /// 中医食物属性
  final List<TCMFoodProperty>? tcmProperties;
  
  /// 治疗效果
  final List<FoodTherapeuticEffect>? therapeuticEffects;
  
  NutrientDatabase({
    required this.name,
    required this.nutrientsPerServing,
    required this.servingSize,
    required this.servingUnit,
    required this.category,
    this.tcmProperties,
    this.therapeuticEffects,
  });
  
  /// 获取特定营养素的含量
  double getNutrientAmount(String nutrientName, double amount) {
    final perServing = nutrientsPerServing[nutrientName] ?? 0;
    return perServing * (amount / servingSize);
  }
}

/// 营养素推荐摄入量
class NutrientRecommendation {
  /// 营养素名称
  final String name;
  
  /// 推荐摄入量
  final double recommendedAmount;
  
  /// 单位
  final String unit;
  
  /// 适用年龄范围起
  final int? ageRangeStart;
  
  /// 适用年龄范围止
  final int? ageRangeEnd;
  
  /// 适用性别
  final String? gender;
  
  /// 特殊生理状态（如怀孕、哺乳等）
  final String? physiologicalState;
  
  /// 上限
  final double? upperLimit;
  
  /// 食物来源示例
  final List<String>? foodSources;
  
  NutrientRecommendation({
    required this.name,
    required this.recommendedAmount,
    required this.unit,
    this.ageRangeStart,
    this.ageRangeEnd,
    this.gender,
    this.physiologicalState,
    this.upperLimit,
    this.foodSources,
  });
}

/// 食品过敏原
enum FoodAllergen {
  /// 牛奶
  milk,
  
  /// 鸡蛋
  eggs,
  
  /// 花生
  peanuts,
  
  /// 树坚果
  treeNuts,
  
  /// 鱼类
  fish,
  
  /// 贝类
  shellfish,
  
  /// 大豆
  soy,
  
  /// 小麦
  wheat,
  
  /// 芹菜
  celery,
  
  /// 芥末
  mustard,
  
  /// 芝麻
  sesame,
  
  /// 二氧化硫和亚硫酸盐
  sulfitesSulfurDioxide,
  
  /// 羽扇豆
  lupin,
  
  /// 软体动物
  molluscs,
}

/// 用户膳食偏好
class DietaryPreference {
  /// 用户ID
  final String userId;
  
  /// 饮食类型
  final DietType dietType;
  
  /// 喜好的食物
  final List<String> preferredFoods;
  
  /// 不喜欢的食物
  final List<String> dislikedFoods;
  
  /// 过敏原
  final List<FoodAllergen> allergens;
  
  /// 最大热量目标（每日）
  final double? targetCalories;
  
  /// 蛋白质目标（每日/克）
  final double? targetProtein;
  
  /// 碳水化合物目标（每日/克）
  final double? targetCarbohydrates;
  
  /// 脂肪目标（每日/克）
  final double? targetFat;
  
  /// 其他饮食限制
  final List<String>? dietaryRestrictions;
  
  /// 健康状况
  final List<String>? healthConditions;
  
  /// 传统中医体质
  final TraditionalChineseBodyType? bodyType;
  
  DietaryPreference({
    required this.userId,
    required this.dietType,
    required this.preferredFoods,
    required this.dislikedFoods,
    required this.allergens,
    this.targetCalories,
    this.targetProtein,
    this.targetCarbohydrates,
    this.targetFat,
    this.dietaryRestrictions,
    this.healthConditions,
    this.bodyType,
  });
  
  /// 转换为Map
  Map<String, dynamic> toMap() {
    return {
      'userId': userId,
      'dietType': dietType.toString().split('.').last,
      'preferredFoods': preferredFoods,
      'dislikedFoods': dislikedFoods,
      'allergens': allergens.map((a) => a.toString().split('.').last).toList(),
      'targetCalories': targetCalories,
      'targetProtein': targetProtein,
      'targetCarbohydrates': targetCarbohydrates,
      'targetFat': targetFat,
      'dietaryRestrictions': dietaryRestrictions,
      'healthConditions': healthConditions,
      'bodyType': bodyType?.toString().split('.').last,
    };
  }
  
  /// 从Map创建
  factory DietaryPreference.fromMap(Map<String, dynamic> map) {
    return DietaryPreference(
      userId: map['userId'],
      dietType: DietType.values.firstWhere(
          (e) => e.toString().split('.').last == map['dietType']),
      preferredFoods: List<String>.from(map['preferredFoods']),
      dislikedFoods: List<String>.from(map['dislikedFoods']),
      allergens: (map['allergens'] as List)
          .map((a) => FoodAllergen.values.firstWhere(
              (e) => e.toString().split('.').last == a))
          .toList(),
      targetCalories: map['targetCalories'],
      targetProtein: map['targetProtein'],
      targetCarbohydrates: map['targetCarbohydrates'],
      targetFat: map['targetFat'],
      dietaryRestrictions: map['dietaryRestrictions'] != null 
          ? List<String>.from(map['dietaryRestrictions']) 
          : null,
      healthConditions: map['healthConditions'] != null 
          ? List<String>.from(map['healthConditions']) 
          : null,
      bodyType: map['bodyType'] != null 
          ? TraditionalChineseBodyType.values.firstWhere(
              (e) => e.toString().split('.').last == map['bodyType']) 
          : null,
    );
  }
}

/// 时间
class TimeOfDay {
  final int hour;
  final int minute;
  
  const TimeOfDay({
    required this.hour,
    required this.minute,
  });
  
  @override
  String toString() {
    final hourString = hour.toString().padLeft(2, '0');
    final minuteString = minute.toString().padLeft(2, '0');
    return '$hourString:$minuteString';
  }
}

/// 营养平衡代理接口
abstract class NutritionBalanceAgent {
  /// 获取代理ID
  String get id;
  
  /// 记录食物摄入
  Future<String> recordFoodIntake(FoodRecord record);
  
  /// 批量记录食物摄入
  Future<List<String>> recordFoodIntakeBatch(List<FoodRecord> records);
  
  /// 获取食物摄入记录
  Future<List<FoodRecord>> getFoodRecords(
    String userId, {
    DateTime? startDate,
    DateTime? endDate,
    String? mealType,
  });
  
  /// 创建营养分析摘要
  Future<NutritionSummary> createNutritionSummary(
    String userId, {
    required DateTime startDate,
    required DateTime endDate,
  });
  
  /// 设置用户饮食偏好
  Future<void> setDietaryPreference(DietaryPreference preference);
  
  /// 获取用户饮食偏好
  Future<DietaryPreference?> getDietaryPreference(String userId);
  
  /// 创建膳食计划
  Future<MealPlan> createMealPlan({
    required String userId,
    required String name,
    required MealPlanType type,
    required DietType dietType,
    required DateTime startDate,
    required int durationInDays,
    double? targetCalories,
    Map<MacronutrientType, double>? macronutrientTargets,
    List<String>? healthGoals,
    List<String>? healthConditions,
    TraditionalChineseBodyType? bodyType,
  });
  
  /// 获取用户膳食计划
  Future<List<MealPlan>> getUserMealPlans(
    String userId, {
    bool? active,
  });
  
  /// 获取膳食计划详情
  Future<MealPlan?> getMealPlanDetail(String mealPlanId);
  
  /// 获取食物营养信息
  Future<Map<String, dynamic>> getFoodNutritionInfo(String foodName, {double? amount, String? unit});
  
  /// 搜索营养数据库
  Future<List<Map<String, dynamic>>> searchNutrientDatabase(
    String query, {
    String? category,
    List<TCMFoodProperty>? tcmProperties,
    List<FoodTherapeuticEffect>? therapeuticEffects,
  });
  
  /// 获取特定健康状况的营养建议
  Future<Map<String, dynamic>> getNutritionAdviceForHealthCondition(
    String healthCondition, {
    String? userId,
    TraditionalChineseBodyType? bodyType,
  });
  
  /// 分析膳食与中医体质的匹配度
  Future<Map<String, dynamic>> analyzeDietBodyTypeCompatibility(
    String userId, {
    TraditionalChineseBodyType? bodyType,
    List<FoodRecord>? foodRecords,
  });
  
  /// 生成每日膳食建议
  Future<DailyMealSchedule> generateDailyMealSuggestion(
    String userId, {
    DateTime? date,
    MealPlanType? planType,
  });
  
  /// 获取营养素推荐摄入量
  Future<List<NutrientRecommendation>> getNutrientRecommendations(
    String userId, {
    double? targetCalories,
    double? targetProtein,
    double? targetCarbohydrates,
    double? targetFat,
    double? targetCalcium,
    double? targetIron,
    double? targetZinc,
    double? targetMagnesium,
    double? targetPotassium,
    double? targetSelenium,
    double? targetChromium,
    double? targetIodine,
  });
}
  
  /// 营养平衡代理实现类
class NutritionBalanceAgentImpl implements NutritionBalanceAgent {
  final AIAgent _agent;
  final AutonomousLearningSystem _learningSystem;
  final RAGService _ragService;
  final SecurityPrivacyFramework _securityFramework;
  final MedicinalFoodAgent _medicinalFoodAgent;
  final KnowledgeGraphAgent _knowledgeGraphAgent;
  
  /// 内部存储
  final Map<String, List<FoodRecord>> _foodRecords = {};
  final Map<String, DietaryPreference> _dietaryPreferences = {};
  final Map<String, List<MealPlan>> _mealPlans = {};
  final List<NutrientDatabase> _nutrientDatabase = [];
  
  /// 构造函数
  NutritionBalanceAgentImpl({
    required AIAgent agent,
    required AutonomousLearningSystem learningSystem,
    required RAGService ragService,
    required SecurityPrivacyFramework securityFramework,
    required MedicinalFoodAgent medicinalFoodAgent,
    required KnowledgeGraphAgent knowledgeGraphAgent,
  }) : 
    _agent = agent,
    _learningSystem = learningSystem,
    _ragService = ragService,
    _securityFramework = securityFramework,
    _medicinalFoodAgent = medicinalFoodAgent,
    _knowledgeGraphAgent = knowledgeGraphAgent {
    _initializeNutrientDatabase();
  }
  
  /// 初始化营养素数据库
  void _initializeNutrientDatabase() {
    // 在实际应用中，这里应该从本地数据库或远程API加载数据
    // 这里仅添加一些示例数据
    _nutrientDatabase.addAll([
      NutrientDatabase(
        name: '大米',
        nutrientsPerServing: {
          'calories': 130.0,
          'protein': 2.7,
          'carbohydrates': 28.0,
          'fat': 0.3,
          'fiber': 0.4,
          'vitaminB1': 0.07,
          'vitaminB2': 0.01,
          'niacin': 1.6,
          'calcium': 10.0,
          'phosphorus': 43.0,
          'iron': 0.2,
          'zinc': 0.6,
        },
        servingSize: 100,
        servingUnit: '克',
        category: '主食',
        tcmProperties: [TCMFoodProperty.neutral, TCMFoodProperty.sweet],
        therapeuticEffects: [FoodTherapeuticEffect.strengthenSpleen, FoodTherapeuticEffect.nourish],
      ),
      NutrientDatabase(
        name: '猪瘦肉',
        nutrientsPerServing: {
          'calories': 143.0,
          'protein': 20.7,
          'carbohydrates': 0.0,
          'fat': 6.3,
          'cholesterol': 70.0,
          'vitaminB1': 0.87,
          'vitaminB2': 0.18,
          'niacin': 4.8,
          'calcium': 6.0,
          'phosphorus': 160.0,
          'iron': 1.5,
          'zinc': 2.1,
        },
        servingSize: 100,
        servingUnit: '克',
        category: '肉类',
        tcmProperties: [TCMFoodProperty.neutral, TCMFoodProperty.sweet, TCMFoodProperty.salty],
        therapeuticEffects: [FoodTherapeuticEffect.tonifyQi, FoodTherapeuticEffect.nourish],
      ),
      // 在实际应用中，应该添加更多食物数据
    ]);
  }
  
  @override
  String get id => _agent.id;
  
  @override
  Future<String> recordFoodIntake(FoodRecord record) async {
    try {
      // 记录安全审计
      await _securityFramework.logSecurityAudit(
        operation: 'RECORD_FOOD_INTAKE',
        parameters: {'userId': record.userId, 'foodName': record.name},
        agentId: id,
      );
      
      // 添加到内部存储
      _foodRecords.putIfAbsent(record.userId, () => []).add(record);
      
      // 记录学习数据
      await _learningSystem.collectData(LearningDataItem(
        id: record.id,
        type: LearningDataType.structured,
        source: LearningDataSource.userInput,
        content: record.toMap(),
        agentId: id,
        userId: record.userId,
      ));
      
      // 发布代理事件
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.dataUpdate,
        source: id,
        data: {
          'operation': 'recordFoodIntake',
          'userId': record.userId,
          'recordId': record.id,
        },
      ));
      
      return record.id;
    } catch (e) {
      if (kDebugMode) {
        print('记录食物摄入失败: $e');
      }
      
      // 发布错误事件
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'recordFoodIntake',
          'error': e.toString(),
        },
      ));
      
      rethrow;
    }
  }
  
  @override
  Future<List<String>> recordFoodIntakeBatch(List<FoodRecord> records) async {
    try {
      final List<String> ids = [];
      
      for (final record in records) {
        ids.add(await recordFoodIntake(record));
      }
      
      return ids;
    } catch (e) {
      if (kDebugMode) {
        print('批量记录食物摄入失败: $e');
      }
      
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'recordFoodIntakeBatch',
          'error': e.toString(),
        },
      ));
      
      rethrow;
    }
  }
  
  @override
  Future<List<FoodRecord>> getFoodRecords(
    String userId, {
    DateTime? startDate,
    DateTime? endDate,
    String? mealType,
  }) async {
    try {
      // 记录安全审计
      await _securityFramework.logSecurityAudit(
        operation: 'GET_FOOD_RECORDS',
        parameters: {'userId': userId},
        agentId: id,
      );
      
      final userRecords = _foodRecords[userId] ?? [];
      
      return userRecords.where((record) {
        if (startDate != null && record.timestamp.isBefore(startDate)) return false;
        if (endDate != null && record.timestamp.isAfter(endDate)) return false;
        if (mealType != null && record.mealType != mealType) return false;
        
        return true;
      }).toList();
    } catch (e) {
      if (kDebugMode) {
        print('获取食物记录失败: $e');
      }
      
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'getFoodRecords',
          'error': e.toString(),
        },
      ));
      
      return [];
    }
  }
  
  @override
  Future<NutritionSummary> createNutritionSummary(
    String userId, {
    required DateTime startDate,
    required DateTime endDate,
  }) async {
    try {
      // 获取该时间段内的所有食物记录
      final records = await getFoodRecords(
        userId,
        startDate: startDate,
        endDate: endDate,
      );
      
      if (records.isEmpty) {
        throw Exception('没有找到该时间段内的食物记录');
      }
      
      // 计算总热量和宏量营养素
      double totalCalories = 0;
      double totalProtein = 0;
      double totalCarbohydrates = 0;
      double totalFat = 0;
      double totalFiber = 0;
      
      // 微量营养素汇总
      final Map<String, double> micronutrientTotals = {};
      
      // 统计每一条记录
      for (final record in records) {
        totalCalories += record.calories;
        totalProtein += record.protein;
        totalCarbohydrates += record.carbohydrates;
        totalFat += record.fat;
        totalFiber += record.fiber ?? 0;
        
        if (record.micronutrients != null) {
          record.micronutrients!.forEach((key, value) {
            micronutrientTotals[key] = (micronutrientTotals[key] ?? 0) + value;
          });
        }
      }
      
      // 获取用户的推荐营养摄入量
      final recommendations = await getNutrientRecommendations(userId);
      final daysCount = endDate.difference(startDate).inDays + 1;
      
      // 创建营养素摄入列表
      final nutrientIntakes = <NutrientIntake>[];
      
      // 创建主要宏量营养素的摄入量对象
      nutrientIntakes.add(NutrientIntake(
        name: '蛋白质',
        amount: totalProtein / daysCount, // 转换为每日平均摄入量
        unit: '克',
        recommendedAmount: _getRecommendedNutrient(recommendations, '蛋白质') ?? 55.0,
        upperLimit: _getRecommendedNutrient(recommendations, '蛋白质', isUpperLimit: true),
      ));
      
      nutrientIntakes.add(NutrientIntake(
        name: '碳水化合物',
        amount: totalCarbohydrates / daysCount,
        unit: '克',
        recommendedAmount: _getRecommendedNutrient(recommendations, '碳水化合物') ?? 250.0,
        upperLimit: _getRecommendedNutrient(recommendations, '碳水化合物', isUpperLimit: true),
      ));
      
      nutrientIntakes.add(NutrientIntake(
        name: '脂肪',
        amount: totalFat / daysCount,
        unit: '克',
        recommendedAmount: _getRecommendedNutrient(recommendations, '脂肪') ?? 60.0,
        upperLimit: _getRecommendedNutrient(recommendations, '脂肪', isUpperLimit: true),
      ));
      
      nutrientIntakes.add(NutrientIntake(
        name: '纤维素',
        amount: totalFiber / daysCount,
        unit: '克',
        recommendedAmount: _getRecommendedNutrient(recommendations, '纤维素') ?? 25.0,
        upperLimit: _getRecommendedNutrient(recommendations, '纤维素', isUpperLimit: true),
      ));
      
      // 添加微量营养素的摄入量对象
      micronutrientTotals.forEach((name, total) {
        final recommendedAmount = _getRecommendedNutrient(recommendations, name);
        if (recommendedAmount != null) {
          nutrientIntakes.add(NutrientIntake(
            name: name,
            amount: total / daysCount,
            unit: _getNutrientUnit(name),
            recommendedAmount: recommendedAmount,
            upperLimit: _getRecommendedNutrient(recommendations, name, isUpperLimit: true),
          ));
        }
      });
      
      // 分析营养不平衡问题
      final nutritionalImbalances = _analyzeNutritionalImbalances(nutrientIntakes);
      
      // 根据不平衡问题生成改善建议
      final improvementSuggestions = await _generateImprovementSuggestions(
        userId,
        nutritionalImbalances,
        nutrientIntakes,
      );
      
      // 计算营养评分
      final nutritionScore = _calculateNutritionScore(nutrientIntakes);
      
      // 创建并返回营养摘要
      return NutritionSummary(
        totalCalories: totalCalories / daysCount,
        totalProtein: totalProtein / daysCount,
        totalCarbohydrates: totalCarbohydrates / daysCount,
        totalFat: totalFat / daysCount,
        totalFiber: totalFiber / daysCount,
        nutrientIntakes: nutrientIntakes,
        startDate: startDate,
        endDate: endDate,
        userId: userId,
        nutritionScore: nutritionScore,
        nutritionalImbalances: nutritionalImbalances,
        improvementSuggestions: improvementSuggestions,
      );
    } catch (e) {
      if (kDebugMode) {
        print('创建营养摘要失败: $e');
      }
      
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'createNutritionSummary',
          'error': e.toString(),
        },
      ));
      
      rethrow;
    }
  }
  
  @override
  Future<void> setDietaryPreference(DietaryPreference preference) async {
    try {
      // 记录安全审计
      await _securityFramework.logSecurityAudit(
        operation: 'SET_DIETARY_PREFERENCE',
        parameters: {'userId': preference.userId},
        agentId: id,
      );
      
      // 存储饮食偏好
      _dietaryPreferences[preference.userId] = preference;
      
      // 记录学习数据
      await _learningSystem.collectData(LearningDataItem(
        id: 'pref_${preference.userId}_${DateTime.now().millisecondsSinceEpoch}',
        type: LearningDataType.structured,
        source: LearningDataSource.userInput,
        content: preference.toMap(),
        agentId: id,
        userId: preference.userId,
      ));
      
      // 发布代理事件
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.dataUpdate,
        source: id,
        data: {
          'operation': 'setDietaryPreference',
          'userId': preference.userId,
        },
      ));
    } catch (e) {
      if (kDebugMode) {
        print('设置饮食偏好失败: $e');
      }
      
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'setDietaryPreference',
          'error': e.toString(),
        },
      ));
      
      rethrow;
    }
  }
  
  @override
  Future<DietaryPreference?> getDietaryPreference(String userId) async {
    try {
      // 记录安全审计
      await _securityFramework.logSecurityAudit(
        operation: 'GET_DIETARY_PREFERENCE',
        parameters: {'userId': userId},
        agentId: id,
      );
      
      return _dietaryPreferences[userId];
    } catch (e) {
      if (kDebugMode) {
        print('获取饮食偏好失败: $e');
      }
      
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'getDietaryPreference',
          'error': e.toString(),
        },
      ));
      
      return null;
    }
  }
  
  @override
  Future<MealPlan> createMealPlan({
    required String userId,
    required String name,
    required MealPlanType type,
    required DietType dietType,
    required DateTime startDate,
    required int durationInDays,
    double? targetCalories,
    Map<MacronutrientType, double>? macronutrientTargets,
    List<String>? healthGoals,
    List<String>? healthConditions,
    TraditionalChineseBodyType? bodyType,
  }) async {
    try {
      // 记录安全审计
      await _securityFramework.logSecurityAudit(
        operation: 'CREATE_MEAL_PLAN',
        parameters: {'userId': userId, 'planType': type.toString()},
        agentId: id,
      );
      
      // 获取用户的饮食偏好
      final preference = await getDietaryPreference(userId);
      
      // 如果未指定目标热量，使用偏好中的目标或默认值
      final calories = targetCalories ?? 
                       preference?.targetCalories ?? 
                       _getDefaultCalories(type, bodyType);
      
      // 如果未指定宏量营养素目标，使用偏好中的目标或默认值
      final protein = macronutrientTargets?[MacronutrientType.protein] ?? 
                     preference?.targetProtein ?? 
                     _getDefaultProtein(calories, type);
                     
      final carbs = macronutrientTargets?[MacronutrientType.carbohydrate] ?? 
                   preference?.targetCarbohydrates ?? 
                   _getDefaultCarbs(calories, type);
                   
      final fat = macronutrientTargets?[MacronutrientType.fat] ?? 
                 preference?.targetFat ?? 
                 _getDefaultFat(calories, type);
      
      // 生成计划ID
      final planId = 'plan_${userId}_${DateTime.now().millisecondsSinceEpoch}';
      
      // 计算结束日期
      final endDate = startDate.add(Duration(days: durationInDays - 1));
      
      // 生成每日膳食安排
      final mealSchedules = await _generateMealSchedules(
        userId,
        startDate,
        durationInDays,
        calories,
        protein,
        carbs,
        fat,
        type,
        dietType,
        preference,
        bodyType,
        healthConditions,
      );
      
      // 生成个性化建议
      final recommendations = await _generatePersonalizedRecommendations(
        userId,
        type,
        dietType,
        bodyType,
        healthConditions,
      );
      
      // 创建膳食计划
      final mealPlan = MealPlan(
        id: planId,
        userId: userId,
        name: name,
        type: type,
        dietType: dietType,
        targetCalories: calories,
        targetProtein: protein,
        targetCarbohydrates: carbs,
        targetFat: fat,
        startDate: startDate,
        endDate: endDate,
        mealSchedules: mealSchedules,
        notes: _generatePlanNotes(type, dietType, bodyType),
        personalizedRecommendations: recommendations,
        healthGoals: healthGoals,
        healthConditions: healthConditions,
        bodyType: bodyType,
      );
      
      // 存储膳食计划
      _mealPlans.putIfAbsent(userId, () => []).add(mealPlan);
      
      // 记录学习数据
      await _learningSystem.collectData(LearningDataItem(
        id: planId,
        type: LearningDataType.structured,
        source: LearningDataSource.agentGenerated,
        content: mealPlan.toMap(),
        agentId: id,
        userId: userId,
      ));
      
      // 发布代理事件
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.dataUpdate,
        source: id,
        data: {
          'operation': 'createMealPlan',
          'userId': userId,
          'planId': planId,
        },
      ));
      
      return mealPlan;
    } catch (e) {
      if (kDebugMode) {
        print('创建膳食计划失败: $e');
      }
      
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'createMealPlan',
          'error': e.toString(),
        },
      ));
      
      rethrow;
    }
  }
  
  @override
  Future<List<MealPlan>> getUserMealPlans(
    String userId, {
    bool? active,
  }) async {
    try {
      // 记录安全审计
      await _securityFramework.logSecurityAudit(
        operation: 'GET_USER_MEAL_PLANS',
        parameters: {'userId': userId},
        agentId: id,
      );
      
      final userPlans = _mealPlans[userId] ?? [];
      
      if (active == null) {
        return userPlans;
      }
      
      final now = DateTime.now();
      
      return userPlans.where((plan) {
        final isActive = now.isAfter(plan.startDate) && now.isBefore(plan.endDate);
        return active ? isActive : !isActive;
      }).toList();
    } catch (e) {
      if (kDebugMode) {
        print('获取用户膳食计划失败: $e');
      }
      
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'getUserMealPlans',
          'error': e.toString(),
        },
      ));
      
      return [];
    }
  }
  
  @override
  Future<MealPlan?> getMealPlanDetail(String mealPlanId) async {
    try {
      // 遍历所有用户的计划
      for (final plans in _mealPlans.values) {
        for (final plan in plans) {
          if (plan.id == mealPlanId) {
            // 记录安全审计
            await _securityFramework.logSecurityAudit(
              operation: 'GET_MEAL_PLAN_DETAIL',
              parameters: {'planId': mealPlanId},
              agentId: id,
            );
            
            return plan;
          }
        }
      }
      
      return null;
    } catch (e) {
      if (kDebugMode) {
        print('获取膳食计划详情失败: $e');
      }
      
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'getMealPlanDetail',
          'error': e.toString(),
        },
      ));
      
      return null;
    }
  }
  
  @override
  Future<Map<String, dynamic>> getFoodNutritionInfo(
    String foodName, {
    double? amount,
    String? unit,
  }) async {
    try {
      // 在营养数据库中查找食物
      final food = _nutrientDatabase.firstWhere(
        (food) => food.name.toLowerCase() == foodName.toLowerCase(),
        orElse: () => throw Exception('未找到食物: $foodName'),
      );
      
      // 默认使用100克/毫升
      final calculatedAmount = amount ?? 100;
      final calculatedUnit = unit ?? food.servingUnit;
      
      // 如果单位不同，需要转换（这里简化处理，实际应用中需要更复杂的单位转换）
      double conversionFactor = 1.0;
      if (calculatedUnit != food.servingUnit) {
        // 这里应该有更复杂的单位转换逻辑
        // 例如从克到盎司，或者从毫升到杯
        // 暂时假设单位相同或者已经转换好
      }
      
      // 计算比例因子（相对于服务尺寸）
      final ratio = (calculatedAmount * conversionFactor) / food.servingSize;
      
      // 准备营养信息
      final Map<String, dynamic> nutritionInfo = {
        'name': food.name,
        'amount': calculatedAmount,
        'unit': calculatedUnit,
        'nutrients': <String, dynamic>{},
      };
      
      // 计算所有营养素的量
      food.nutrientsPerServing.forEach((nutrient, value) {
        nutritionInfo['nutrients'][nutrient] = value * ratio;
      });
      
      // 添加中医食疗属性和治疗效果
      if (food.tcmProperties != null) {
        nutritionInfo['tcmProperties'] = food.tcmProperties!
            .map((prop) => prop.toString().split('.').last)
            .toList();
      }
      
      if (food.therapeuticEffects != null) {
        nutritionInfo['therapeuticEffects'] = food.therapeuticEffects!
            .map((effect) => effect.toString().split('.').last)
            .toList();
      }
      
      return nutritionInfo;
    } catch (e) {
      if (kDebugMode) {
        print('获取食物营养信息失败: $e');
      }
      
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'getFoodNutritionInfo',
          'error': e.toString(),
        },
      ));
      
      // 返回空信息而不是抛出异常
      return {
        'name': foodName,
        'error': '未找到此食物的营养信息',
      };
    }
  }
  
  @override
  Future<List<Map<String, dynamic>>> searchNutrientDatabase(
    String query, {
    String? category,
    List<TCMFoodProperty>? tcmProperties,
    List<FoodTherapeuticEffect>? therapeuticEffects,
  }) async {
    try {
      final results = _nutrientDatabase.where((food) {
        // 名称匹配
        if (!food.name.toLowerCase().contains(query.toLowerCase())) {
          return false;
        }
        
        // 分类匹配
        if (category != null && food.category != category) {
          return false;
        }
        
        // 中医属性匹配
        if (tcmProperties != null && tcmProperties.isNotEmpty) {
          if (food.tcmProperties == null) return false;
          
          for (final property in tcmProperties) {
            if (!food.tcmProperties!.contains(property)) {
              return false;
            }
          }
        }
        
        // 治疗效果匹配
        if (therapeuticEffects != null && therapeuticEffects.isNotEmpty) {
          if (food.therapeuticEffects == null) return false;
          
          for (final effect in therapeuticEffects) {
            if (!food.therapeuticEffects!.contains(effect)) {
              return false;
            }
          }
        }
        
        return true;
      }).map((food) {
        // 转换为简化的Map结构
        return {
          'name': food.name,
          'category': food.category,
          'servingSize': food.servingSize,
          'servingUnit': food.servingUnit,
          'calories': food.nutrientsPerServing['calories'] ?? 0,
          'protein': food.nutrientsPerServing['protein'] ?? 0,
          'carbohydrates': food.nutrientsPerServing['carbohydrates'] ?? 0,
          'fat': food.nutrientsPerServing['fat'] ?? 0,
          'tcmProperties': food.tcmProperties?.map((p) => p.toString().split('.').last).toList(),
          'therapeuticEffects': food.therapeuticEffects?.map((e) => e.toString().split('.').last).toList(),
        };
      }).toList();
      
      return results;
    } catch (e) {
      if (kDebugMode) {
        print('搜索营养数据库失败: $e');
      }
      
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'searchNutrientDatabase',
          'error': e.toString(),
        },
      ));
      
      return [];
    }
  }
  
  @override
  Future<Map<String, dynamic>> getNutritionAdviceForHealthCondition(
    String healthCondition, {
    String? userId,
    TraditionalChineseBodyType? bodyType,
  }) async {
    try {
      // 使用RAG服务查询相关知识
      final query = '营养建议 $healthCondition';
      
      // 获取相关健康知识
      final ragResults = await _ragService.query(
        query,
        RAGType.directRetrieval,
        RAGQueryOptions(
          collection: 'health_knowledge',
          minScore: 0.7,
        ),
      );
      
      // 如果有用户ID，尝试获取用户的饮食偏好
      DietaryPreference? preference;
      if (userId != null) {
        preference = await getDietaryPreference(userId);
      }
      
      // 获取相关食材建议
      List<Map<String, dynamic>> recommendedFoods = [];
      
      // 如果有药食同源代理，尝试获取推荐食材
      try {
        final bodyTypeToUse = bodyType ?? preference?.bodyType;
        final healthConditions = [healthCondition];
        
        if (bodyTypeToUse != null) {
          final foodResults = await _medicinalFoodAgent.getRecommendedFoodsForHealthConditions(
            healthConditions,
            bodyType: bodyTypeToUse,
            userId: userId,
          );
          
          // 转换为简化结构
          recommendedFoods = foodResults.map((result) => {
            'name': result.food.name,
            'score': result.overallRecommendationScore,
            'reasons': result.recommendationReasons,
            'usage': result.suggestedUsage,
            'precautions': result.precautions,
          }).toList();
        }
      } catch (e) {
        if (kDebugMode) {
          print('获取推荐食材失败: $e');
        }
      }
      
      // 构建最终建议
      return {
        'healthCondition': healthCondition,
        'generalAdvice': ragResults.isNotEmpty 
            ? ragResults.map((r) => r.content).join('\n\n')
            : '未找到相关营养建议',
        'recommendedFoods': recommendedFoods,
        'dietaryPrinciples': _generateDietaryPrinciples(healthCondition, bodyType),
        'avoidedFoods': _generateAvoidedFoods(healthCondition, bodyType),
        'mealPatterns': _generateMealPatterns(healthCondition, bodyType),
      };
    } catch (e) {
      if (kDebugMode) {
        print('获取健康状况营养建议失败: $e');
      }
      
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'getNutritionAdviceForHealthCondition',
          'error': e.toString(),
        },
      ));
      
      // 返回基本结构而不是抛出异常
      return {
        'healthCondition': healthCondition,
        'generalAdvice': '获取建议时出错',
        'recommendedFoods': [],
        'dietaryPrinciples': [],
        'avoidedFoods': [],
        'mealPatterns': [],
        'error': e.toString(),
      };
    }
  }
  
  @override
  Future<Map<String, dynamic>> analyzeDietBodyTypeCompatibility(
    String userId, {
    TraditionalChineseBodyType? bodyType,
    List<FoodRecord>? foodRecords,
  }) async {
    try {
      // 确定体质类型
      TraditionalChineseBodyType? userBodyType = bodyType;
      
      // 如果未提供体质类型，尝试从用户偏好中获取
      if (userBodyType == null) {
        final preference = await getDietaryPreference(userId);
        userBodyType = preference?.bodyType;
      }
      
      // 如果仍未确定体质类型，返回错误
      if (userBodyType == null) {
        throw Exception('未指定体质类型');
      }
      
      // 获取食物记录
      final records = foodRecords ?? 
                      await getFoodRecords(
                        userId,
                        startDate: DateTime.now().subtract(Duration(days: 7)),
                      );
      
      // 分析每种食物与体质的兼容性
      final foodCompatibility = <Map<String, dynamic>>[];
      
      for (final record in records) {
        // 获取食物的中医属性
        final tcmProperties = record.tcmProperties ?? [];
        
        // 计算兼容性分数（这里使用简化的评分逻辑）
        int compatibilityScore = _calculateFoodBodyTypeCompatibility(tcmProperties, userBodyType);
        
        // 确定兼容性级别
        String compatibilityLevel;
        if (compatibilityScore >= 80) {
          compatibilityLevel = '非常适合';
        } else if (compatibilityScore >= 60) {
          compatibilityLevel = '适合';
        } else if (compatibilityScore >= 40) {
          compatibilityLevel = '一般';
        } else if (compatibilityScore >= 20) {
          compatibilityLevel = '不太适合';
        } else {
          compatibilityLevel = '不适合';
        }
        
        // 添加到结果列表
        foodCompatibility.add({
          'foodName': record.name,
          'compatibilityScore': compatibilityScore,
          'compatibilityLevel': compatibilityLevel,
          'properties': tcmProperties.map((p) => p.toString().split('.').last).toList(),
          'amount': record.amount,
          'unit': record.unit,
        });
      }
      
      // 获取适合该体质的推荐食物
      final recommendedFoods = await _medicinalFoodAgent.getRecommendedFoodsForBodyType(userBodyType);
      
      // 转换为简化结构
      final recommendations = recommendedFoods.map((food) => {
        'name': food.name,
        'properties': food.properties.map((p) => p.toString().split('.').last).toList(),
        'effects': food.therapeuticEffects.map((e) => e.toString().split('.').last).toList(),
      }).toList();
      
      // 获取体质调理指南
      final adjustmentGuidelines = await _medicinalFoodAgent.getBodyTypeAdjustmentGuidelines();
      final guidelines = adjustmentGuidelines[userBodyType] ?? [];
      
      // 构建最终分析结果
      return {
        'userId': userId,
        'bodyType': userBodyType.toString().split('.').last,
        'overallCompatibility': _calculateOverallCompatibility(foodCompatibility),
        'foodCompatibility': foodCompatibility,
        'recommendedFoods': recommendations,
        'adjustmentGuidelines': guidelines,
        'seasonalSuggestions': _getSeasonalSuggestions(userBodyType),
      };
    } catch (e) {
      if (kDebugMode) {
        print('分析膳食与体质匹配度失败: $e');
      }
      
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'analyzeDietBodyTypeCompatibility',
          'error': e.toString(),
        },
      ));
      
      // 返回基本结构而不是抛出异常
      return {
        'userId': userId,
        'bodyType': bodyType?.toString().split('.').last ?? '未知',
        'overallCompatibility': 0,
        'foodCompatibility': [],
        'recommendedFoods': [],
      };
    }
  }
  
  @override
  Future<DailyMealSchedule> generateDailyMealSuggestion(
    String userId, {
    DateTime? date,
    MealPlanType? planType,
  }) async {
    try {
      final currentDate = date ?? DateTime.now();
      
      // 获取用户的饮食偏好
      final preference = await getDietaryPreference(userId);
      
      // 获取用户的活跃膳食计划
      final activePlans = await getUserMealPlans(userId, active: true);
      
      // 如果用户有活跃的膳食计划且类型匹配，使用该计划
      MealPlan? selectedPlan;
      if (activePlans.isNotEmpty) {
        if (planType != null) {
          selectedPlan = activePlans.firstWhere(
            (plan) => plan.type == planType,
            orElse: () => activePlans.first,
          );
        } else {
          selectedPlan = activePlans.first;
        }
        
        // 查找当日膳食安排
        for (final schedule in selectedPlan.mealSchedules) {
          if (schedule.date.year == currentDate.year &&
              schedule.date.month == currentDate.month &&
              schedule.date.day == currentDate.day) {
            return schedule;
          }
        }
      }
      
      // 如果没有找到匹配的膳食安排，生成一个新的
      final dietType = preference?.dietType ?? DietType.regular;
      final bodyType = preference?.bodyType;
      
      // 确定膳食计划类型
      final mealPlanType = planType ?? MealPlanType.maintenance;
      
      // 确定目标热量和宏量营养素
      final targetCalories = preference?.targetCalories ?? _getDefaultCalories(mealPlanType, bodyType);
      final targetProtein = preference?.targetProtein ?? _getDefaultProtein(targetCalories, mealPlanType);
      final targetCarbs = preference?.targetCarbohydrates ?? _getDefaultCarbs(targetCalories, mealPlanType);
      final targetFat = preference?.targetFat ?? _getDefaultFat(targetCalories, mealPlanType);
      
      // 查询季节性食物
      final season = _getCurrentSeason(currentDate);
      final seasonalFoods = await _medicinalFoodAgent.getSeasonalProducts(season);
      
      // 生成膳食
      final breakfast = await _generateMeal(
        'breakfast',
        '早餐',
        TimeOfDay(hour: 7, minute: 30),
        targetCalories * 0.25,
        targetProtein * 0.2,
        targetCarbs * 0.3,
        targetFat * 0.2,
        dietType,
        bodyType,
        preference,
        seasonalFoods,
      );
      
      final lunch = await _generateMeal(
        'lunch',
        '午餐',
        TimeOfDay(hour: 12, minute: 0),
        targetCalories * 0.35,
        targetProtein * 0.4,
        targetCarbs * 0.4,
        targetFat * 0.3,
        dietType,
        bodyType,
        preference,
        seasonalFoods,
      );
      
      final dinner = await _generateMeal(
        'dinner',
        '晚餐',
        TimeOfDay(hour: 18, minute: 30),
        targetCalories * 0.3,
        targetProtein * 0.4,
        targetCarbs * 0.3,
        targetFat * 0.4,
        dietType,
        bodyType,
        preference,
        seasonalFoods,
      );
      
      final snack = await _generateMeal(
        'snack',
        '零食',
        TimeOfDay(hour: 15, minute: 0),
        targetCalories * 0.1,
        targetProtein * 0.0,
        targetCarbs * 0.0,
        targetFat * 0.1,
        dietType,
        bodyType,
        preference,
        seasonalFoods,
      );
      
      // 创建每日膳食安排
      final dailySchedule = DailyMealSchedule(
        date: currentDate,
        meals: [breakfast, lunch, snack, dinner],
        totalCalories: breakfast.totalCalories + lunch.totalCalories + dinner.totalCalories + snack.totalCalories,
        totalProtein: breakfast.totalProtein + lunch.totalProtein + dinner.totalProtein + snack.totalProtein,
        totalCarbohydrates: breakfast.totalCarbohydrates + lunch.totalCarbohydrates + dinner.totalCarbohydrates + snack.totalCarbohydrates,
        totalFat: breakfast.totalFat + lunch.totalFat + dinner.totalFat + snack.totalFat,
        specialInstructions: _generateSpecialInstructions(currentDate, bodyType),
        seasonalAdjustment: _generateSeasonalAdjustment(season, bodyType),
      );
      
      return dailySchedule;
    } catch (e) {
      if (kDebugMode) {
        print('生成每日膳食建议失败: $e');
      }
      
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'generateDailyMealSuggestion',
          'error': e.toString(),
        },
      ));
      
      // 创建默认的膳食安排
      return _createDefaultDailyMealSchedule(date ?? DateTime.now());
    }
  }
  
  @override
  Future<List<NutrientRecommendation>> getNutrientRecommendations(
    String userId, {
    double? targetCalories,
    double? targetProtein,
    double? targetCarbohydrates,
    double? targetFat,
    double? targetCalcium,
    double? targetIron,
    double? targetZinc,
    double? targetMagnesium,
    double? targetPotassium,
    double? targetSelenium,
    double? targetChromium,
    double? targetIodine,
  }) async {
    try {
      // 获取用户基本信息以确定推荐值
      // 实际应用中，这里应该根据用户的年龄、性别、体重、活动水平等计算
      // 这里使用简化的推荐值
      
      final List<NutrientRecommendation> recommendations = [];
      
      // 宏量营养素
      recommendations.add(NutrientRecommendation(
        name: '蛋白质',
        recommendedAmount: targetProtein ?? 55.0,
        unit: '克',
        foodSources: ['瘦肉', '鱼', '豆腐', '鸡蛋', '酸奶'],
      ));
      
      recommendations.add(NutrientRecommendation(
        name: '碳水化合物',
        recommendedAmount: targetCarbohydrates ?? 250.0,
        unit: '克',
        upperLimit: 300.0,
        foodSources: ['米饭', '面条', '燕麦', '土豆', '水果'],
      ));
      
      recommendations.add(NutrientRecommendation(
        name: '脂肪',
        recommendedAmount: targetFat ?? 60.0,
        unit: '克',
        upperLimit: 80.0,
        foodSources: ['橄榄油', '坚果', '鱼油', '牛油果'],
      ));
      
      recommendations.add(NutrientRecommendation(
        name: '纤维素',
        recommendedAmount: 25.0,
        unit: '克',
        foodSources: ['全谷物', '豆类', '水果', '蔬菜'],
      ));
      
      // 微量营养素
      recommendations.add(NutrientRecommendation(
        name: '钙',
        recommendedAmount: targetCalcium ?? 1000.0,
        unit: '毫克',
        upperLimit: 2500.0,
        foodSources: ['牛奶', '酸奶', '奶酪', '豆腐', '小鱼干'],
      ));
      
      recommendations.add(NutrientRecommendation(
        name: '铁',
        recommendedAmount: targetIron ?? 18.0,
        unit: '毫克',
        upperLimit: 45.0,
        foodSources: ['红肉', '豆类', '菠菜', '贝类'],
      ));
      
      recommendations.add(NutrientRecommendation(
        name: '锌',
        recommendedAmount: targetZinc ?? 15.0,
        unit: '毫克',
        upperLimit: 40.0,
        foodSources: ['牡蛎', '红肉', '坚果', '全谷物'],
      ));
      
      recommendations.add(NutrientRecommendation(
        name: '镁',
        recommendedAmount: targetMagnesium ?? 400.0,
        unit: '毫克',
        upperLimit: 350.0,
        foodSources: ['绿叶蔬菜', '坚果', '全谷物', '豆类'],
      ));
      
      recommendations.add(NutrientRecommendation(
        name: '钾',
        recommendedAmount: targetPotassium ?? 3500.0,
        unit: '毫克',
        foodSources: ['香蕉', '土豆', '豆类', '菠菜'],
      ));
      
      recommendations.add(NutrientRecommendation(
        name: '硒',
        recommendedAmount: targetSelenium ?? 55.0,
        unit: '微克',
        upperLimit: 400.0,
        foodSources: ['巴西坚果', '金枪鱼', '瘦肉', '全谷物'],
      ));
      
      recommendations.add(NutrientRecommendation(
        name: '铬',
        recommendedAmount: targetChromium ?? 35.0,
        unit: '微克',
        foodSources: ['全谷物', '啤酒酵母', '肉类', '蘑菇'],
      ));
      
      recommendations.add(NutrientRecommendation(
        name: '碘',
        recommendedAmount: targetIodine ?? 150.0,
        unit: '微克',
        upperLimit: 1100.0,
        foodSources: ['海带', '海鱼', '海藻', '碘盐'],
      ));
      
      // 添加维生素
      _addVitaminRecommendations(recommendations);
      
      return recommendations;
    } catch (e) {
      if (kDebugMode) {
        print('获取营养素推荐摄入量失败: $e');
      }
      
      _agent.publishEvent(AgentEvent(
        type: AgentEventType.error,
        source: id,
        data: {
          'operation': 'getNutrientRecommendations',
          'error': e.toString(),
        },
      ));
      
      // 返回基本推荐
      return _getBasicRecommendations();
    }
  }
  
  // 辅助方法
  
  /// 从推荐列表中获取特定营养素的推荐量
  double? _getRecommendedNutrient(List<NutrientRecommendation> recommendations, String name, {bool isUpperLimit = false}) {
    for (final rec in recommendations) {
      if (rec.name == name) {
        return isUpperLimit ? rec.upperLimit : rec.recommendedAmount;
      }
    }
    return null;
  }
  
  /// 获取营养素的单位
  String _getNutrientUnit(String name) {
    if (['蛋白质', '碳水化合物', '脂肪', '纤维素'].contains(name)) {
      return '克';
    } else if (['钙', '镁', '钾', '钠', '铁', '锌', '铜'].contains(name)) {
      return '毫克';
    } else if (['维生素A', '维生素D', '维生素E', '维生素K'].contains(name)) {
      return '微克';
    } else if (['维生素C', '维生素B1', '维生素B2', '维生素B6', '维生素B12', '烟酸', '叶酸'].contains(name)) {
      return '毫克';
    } else {
      return '单位';
    }
  }
  
  /// 根据计划类型和体质获取默认热量
  double _getDefaultCalories(MealPlanType type, TraditionalChineseBodyType? bodyType) {
    switch (type) {
      case MealPlanType.weightLoss:
        return 1500.0;
      case MealPlanType.muscleGain:
        return 2800.0;
      case MealPlanType.maintenance:
        return 2000.0;
      case MealPlanType.energyBoost:
        return 2200.0;
      case MealPlanType.immunityBoost:
        return 2100.0;
      case MealPlanType.digestiveHealth:
        return 1900.0;
      case MealPlanType.sleepImprovement:
        return 1800.0;
      default:
        return 2000.0;
    }
  }
  
  /// 根据热量和计划类型获取默认蛋白质
  double _getDefaultProtein(double calories, MealPlanType type) {
    switch (type) {
      case MealPlanType.muscleGain:
        return calories * 0.3 / 4; // 30% 热量来自蛋白质
      case MealPlanType.weightLoss:
        return calories * 0.35 / 4; // 35% 热量来自蛋白质
      default:
        return calories * 0.2 / 4; // 20% 热量来自蛋白质
    }
  }
  
  /// 根据热量和计划类型获取默认碳水化合物
  double _getDefaultCarbs(double calories, MealPlanType type) {
    switch (type) {
      case MealPlanType.weightLoss:
        return calories * 0.3 / 4; // 30% 热量来自碳水
      case MealPlanType.muscleGain:
        return calories * 0.5 / 4; // 50% 热量来自碳水
      case MealPlanType.energyBoost:
        return calories * 0.55 / 4; // 55% 热量来自碳水
      default:
        return calories * 0.5 / 4; // 50% 热量来自碳水
    }
  }
  
  /// 根据热量和计划类型获取默认脂肪
  double _getDefaultFat(double calories, MealPlanType type) {
    switch (type) {
      case MealPlanType.heartHealth:
        return calories * 0.3 / 9; // 30% 热量来自脂肪
      case MealPlanType.brainHealth:
        return calories * 0.35 / 9; // 35% 热量来自脂肪
      case MealPlanType.weightLoss:
        return calories * 0.35 / 9; // 35% 热量来自脂肪
      default:
        return calories * 0.3 / 9; // 30% 热量来自脂肪
    }
  }
  
  /// 分析营养不平衡问题
  List<String> _analyzeNutritionalImbalances(List<NutrientIntake> intakes) {
    final imbalances = <String>[];
    
    for (final intake in intakes) {
      switch (intake.status) {
        case NutrientIntakeStatus.deficient:
          imbalances.add('${intake.name}严重不足，仅达到推荐量的${(intake.amount / intake.recommendedAmount * 100).toStringAsFixed(0)}%');
          break;
        case NutrientIntakeStatus.suboptimal:
          imbalances.add('${intake.name}略有不足，达到推荐量的${(intake.amount / intake.recommendedAmount * 100).toStringAsFixed(0)}%');
          break;
        case NutrientIntakeStatus.excessive:
          if (intake.upperLimit != null) {
            imbalances.add('${intake.name}摄入过量，超过了安全上限');
          }
          break;
        default:
          // 适宜的或高于最佳但未超过上限的不算作不平衡
          break;
      }
    }
    
    return imbalances;
  }
  
  /// 根据不平衡问题生成改善建议
  Future<List<String>> _generateImprovementSuggestions(
    String userId,
    List<String> imbalances,
    List<NutrientIntake> intakes,
  ) async {
    final suggestions = <String>[];
    
    // 处理营养素不足的情况
    for (final intake in intakes) {
      if (intake.status == NutrientIntakeStatus.deficient || intake.status == NutrientIntakeStatus.suboptimal) {
        final foodSuggestions = await _getFoodSourcesForNutrient(intake.name);
        if (foodSuggestions.isNotEmpty) {
          suggestions.add('增加${intake.name}的摄入：可以多吃${foodSuggestions.join('、')}');
        }
      } else if (intake.status == NutrientIntakeStatus.excessive && intake.upperLimit != null) {
        suggestions.add('减少${intake.name}的摄入，当前摄入量已超过安全上限');
      }
    }
    
    // 添加一些通用建议
    if (suggestions.isEmpty) {
      suggestions.add('总体营养状况良好，请保持均衡饮食');
    } else {
      suggestions.add('建议保持饮食多样化，增加全谷物、新鲜水果和蔬菜的摄入');
      
      // 检查是否可能需要补充剂
      final deficientNutrients = intakes
          .where((i) => i.status == NutrientIntakeStatus.deficient)
          .map((i) => i.name)
          .toList();
          
      if (deficientNutrients.isNotEmpty) {
        suggestions.add('可以考虑在医生指导下补充${deficientNutrients.join('、')}');
      }
    }
    
    return suggestions;
  }
  
  /// 获取特定营养素的食物来源
  Future<List<String>> _getFoodSourcesForNutrient(String nutrientName) async {
    // 可以使用知识图谱代理查询
    try {
      final query = '富含${nutrientName}的食物';
      final results = await _knowledgeGraphAgent.queryKnowledgeGraph(
        query,
        KnowledgeGraphQueryType.foodNutrition,
      );
      
      if (results.isNotEmpty) {
        return List<String>.from(results[0]['foodSources'] ?? []);
      }
    } catch (e) {
      if (kDebugMode) {
        print('获取营养素食物来源失败: $e');
      }
    }
    
    // 返回基础食物来源
    switch (nutrientName) {
      case '蛋白质':
        return ['瘦肉', '鱼', '豆腐', '鸡蛋', '酸奶'];
      case '碳水化合物':
        return ['米饭', '面条', '燕麦', '土豆', '水果'];
      case '脂肪':
        return ['橄榄油', '坚果', '鱼油', '牛油果'];
      case '纤维素':
        return ['全谷物', '豆类', '水果', '蔬菜'];
      case '钙':
        return ['牛奶', '酸奶', '奶酪', '豆腐', '小鱼干'];
      case '铁':
        return ['红肉', '豆类', '菠菜', '贝类'];
      case '锌':
        return ['牡蛎', '红肉', '坚果', '全谷物'];
      case '镁':
        return ['绿叶蔬菜', '坚果', '全谷物', '豆类'];
      case '钾':
        return ['香蕉', '土豆', '豆类', '菠菜'];
      case '硒':
        return ['巴西坚果', '金枪鱼', '瘦肉', '全谷物'];
      case '铬':
        return ['全谷物', '啤酒酵母', '肉类', '蘑菇'];
      case '碘':
        return ['海带', '海鱼', '海藻', '碘盐'];
      default:
        return [];
    }
  }
  
  /// 计算食物与体质的兼容性分数
  int _calculateFoodBodyTypeCompatibility(List<TCMFoodProperty> properties, TraditionalChineseBodyType bodyType) {
    // 这是一个简化的评分逻辑，实际应用中需要更复杂的中医理论支持
    int score = 50; // 基础分
    
    // 根据体质和食物属性调整分数
    if (bodyType == TraditionalChineseBodyType.coldConstitution) {
      // 寒性体质应该避免寒性食物，适合温热性食物
      if (properties.contains(TCMFoodProperty.cold)) {
        score -= 30;
      }
      if (properties.contains(TCMFoodProperty.cool)) {
        score -= 20;
      }
      if (properties.contains(TCMFoodProperty.warm)) {
        score += 20;
      }
      if (properties.contains(TCMFoodProperty.hot)) {
        score += 10; // 过热也不完全适合
      }
    } else if (bodyType == TraditionalChineseBodyType.hotConstitution) {
      // 热性体质应该避免热性食物，适合寒凉性食物
      if (properties.contains(TCMFoodProperty.hot)) {
        score -= 30;
      }
      if (properties.contains(TCMFoodProperty.warm)) {
        score -= 20;
      }
      if (properties.contains(TCMFoodProperty.cool)) {
        score += 20;
      }
      if (properties.contains(TCMFoodProperty.cold)) {
        score += 10; // 过寒也不完全适合
      }
    } else if (bodyType == TraditionalChineseBodyType.dampnessConstitution) {
      // 湿性体质应该避免湿性食物，适合健脾除湿的食物
      if (properties.contains(TCMFoodProperty.damp)) {
        score -= 30;
      }
      if (properties.contains(TCMFoodProperty.dry)) {
        score += 20;
      }
    }
    
    // 限制分数范围
    return max(0, min(100, score));
  }
  
  /// 计算整体兼容性评分
  int _calculateOverallCompatibility(List<Map<String, dynamic>> foodCompatibility) {
    if (foodCompatibility.isEmpty) {
      return 0;
    }
    
    int totalScore = 0;
    for (final foodItem in foodCompatibility) {
      totalScore += foodItem['compatibilityScore'] as int;
    }
    
    return totalScore ~/ foodCompatibility.length;
  }
  
  /// 获取季节性建议
  List<String> _getSeasonalSuggestions(TraditionalChineseBodyType bodyType) {
    final season = _getCurrentSeason(DateTime.now());
    
    switch (bodyType) {
      case TraditionalChineseBodyType.coldConstitution:
        if (season == 'winter') {
          return ['冬季寒性体质更应注意保暖', '可以适量食用羊肉、狗肉等温热食物', '多喝热汤', '避免生冷食物和冷饮'];
        } else if (season == 'summer') {
          return ['夏季注意不要过度贪凉', '避免长时间待在空调房中', '可以食用温性水果如荔枝、龙眼', '早晚可喝生姜红糖水调理'];
        }
        break;
      case TraditionalChineseBodyType.hotConstitution:
        if (season == 'summer') {
          return ['夏季热性体质更应注意清热', '可以适量食用西瓜、苦瓜等清热食物', '多喝菊花茶、绿豆汤', '避免辛辣刺激性食物'];
        } else if (season == 'winter') {
          return ['冬季饮食可略微温和', '避免过于温热的食物', '可以食用梨、银耳等滋阴润肺的食物', '注意保持室内湿度'];
        }
        break;
      case TraditionalChineseBodyType.dampnessConstitution:
        if (season == 'rainy') {
          return ['雨季湿性体质更应注意祛湿', '可以适量食用薏米、赤小豆等利水渗湿食物', '多喝茯苓饮、陈皮茶', '避免肥甘厚腻食物'];
        } else if (season == 'summer') {
          return ['夏季注意避免过度贪凉生湿', '可以食用苦瓜、冬瓜等清热利湿食物', '饮食宜清淡少油', '适当运动促进水分代谢'];
        }
        break;
      default:
        break;
    }
    
    return ['根据季节变化调整饮食', '遵循"春生、夏长、秋收、冬藏"的原则', '选择当季新鲜食材'];
  }
  
  /// 获取当前季节
  String _getCurrentSeason(DateTime date) {
    final month = date.month;
    
    if (month >= 3 && month <= 5) {
      return 'spring';
    } else if (month >= 6 && month <= 8) {
      return 'summer';
    } else if (month >= 9 && month <= 11) {
      return 'autumn';
    } else {
      return 'winter';
    }
  }
  
  /// 生成特定健康状况的饮食原则
  List<String> _generateDietaryPrinciples(String healthCondition, TraditionalChineseBodyType? bodyType) {
    switch (healthCondition.toLowerCase()) {
      case '高血压':
        return ['控制钠盐摄入，每日不超过5克', '增加钾的摄入，多吃新鲜蔬果', '减少动物脂肪摄入', '避免烟酒'];
      case '糖尿病':
        return ['控制总热量摄入', '选择低升糖指数食物', '控制单糖和淀粉摄入', '增加膳食纤维摄入', '定时定量进餐'];
      case '脂肪肝':
        return ['控制总热量摄入', '减少油脂摄入', '增加优质蛋白质', '多吃新鲜蔬菜和水果', '避免饮酒'];
      case '贫血':
        return ['增加含铁丰富的食物', '搭配维生素C促进铁吸收', '适量增加动物性食品', '保证足够蛋白质摄入'];
      default:
        return ['保持饮食多样化', '控制总热量', '减少精制食品摄入', '增加膳食纤维'];
    }
  }
  
  /// 生成应避免的食物
  List<String> _generateAvoidedFoods(String healthCondition, TraditionalChineseBodyType? bodyType) {
    switch (healthCondition.toLowerCase()) {
      case '高血压':
        return ['腌制食品', '加工肉制品', '高盐零食', '酒精饮料'];
      case '糖尿病':
        return ['精制糖', '甜点', '含糖饮料', '白面包', '精白米'];
      case '脂肪肝':
        return ['油炸食品', '高脂肪肉类', '甜点', '酒精饮料', '含糖饮料'];
      case '贫血':
        return ['浓茶', '咖啡', '碳酸饮料', '过多膳食纤维'];
      default:
        return ['过度加工食品', '反式脂肪', '过多添加糖', '过多盐分'];
    }
  }
  
  /// 生成膳食模式
  List<String> _generateMealPatterns(String healthCondition, TraditionalChineseBodyType? bodyType) {
    switch (healthCondition.toLowerCase()) {
      case '高血压':
        return ['DASH饮食模式', '地中海饮食模式', '少量多餐', '晚餐宜清淡'];
      case '糖尿病':
        return ['控制碳水化合物分配', '三餐规律', '适量加餐', '晚餐避免过晚'];
      case '脂肪肝':
        return ['控制总热量', '早餐丰富', '午餐适量', '晚餐清淡', '戒酒'];
      case '贫血':
        return ['三餐规律', '保证优质蛋白质', '搭配富含维生素C的食物', '避免空腹喝茶'];
      default:
        return ['规律三餐', '合理分配', '八分饱原则', '细嚼慢咽'];
    }
  }
  
  /// 生成膳食计划注意事项
  List<String> _generatePlanNotes(MealPlanType type, DietType dietType, TraditionalChineseBodyType? bodyType) {
    final notes = <String>[];
    
    // 根据膳食计划类型添加注意事项
    switch (type) {
      case MealPlanType.weightLoss:
        notes.add('控制总热量摄入，保持适度热量赤字');
        notes.add('保证充足蛋白质摄入，以维持肌肉量');
        notes.add('增加膳食纤维摄入，提高饱腹感');
        break;
      case MealPlanType.muscleGain:
        notes.add('确保足够的蛋白质摄入，分配在各餐中');
        notes.add('保证适度的热量盈余，支持肌肉生长');
        notes.add('训练后及时补充蛋白质和碳水化合物');
        break;
      case MealPlanType.maintenance:
        notes.add('保持均衡饮食，各类营养素比例适当');
        notes.add('注意食物多样化，确保微量营养素充足');
        break;
      case MealPlanType.diseasePrevention:
        notes.add('减少加工食品摄入，选择天然食材');
        notes.add('适当增加抗氧化物质摄入，如新鲜蔬果');
        break;
      default:
        notes.add('保持规律进餐，细嚼慢咽');
        notes.add('选择新鲜食材，减少加工食品');
        break;
    }
    
    // 根据饮食类型添加注意事项
    switch (dietType) {
      case DietType.vegetarian:
        notes.add('注意补充维生素B12和优质蛋白质');
        notes.add('可以考虑添加奶制品和鸡蛋，提高营养完整性');
        break;
      case DietType.vegan:
        notes.add('需要额外补充维生素B12、钙、铁和锌');
        notes.add('注意蛋白质组合，确保必需氨基酸完整');
        break;
      case DietType.lowCarb:
        notes.add('选择低淀粉高纤维的蔬菜');
        notes.add('确保足够的优质脂肪摄入');
        break;
      case DietType.keto:
        notes.add('摄入充足水分和电解质，预防酮症状');
        notes.add('确保足够膳食纤维，预防便秘');
        break;
      case DietType.tcmDiet:
        notes.add('根据体质和季节调整食物温性');
        notes.add('遵循"药食同源"原则，调理身体');
        break;
      default:
        break;
    }
    
    // 根据体质添加注意事项
    if (bodyType != null) {
      switch (bodyType) {
        case TraditionalChineseBodyType.coldConstitution:
          notes.add('宜食用温热性食物，避免寒凉食物');
          notes.add('可适当添加生姜、桂皮等温性调料');
          break;
        case TraditionalChineseBodyType.hotConstitution:
          notes.add('宜食用凉性食物，避免温热性食物');
          notes.add('可适当添加薄荷、菊花等凉性茶饮');
          break;
        case TraditionalChineseBodyType.dampnessConstitution:
          notes.add('宜食用健脾祛湿食物，避免生冷黏腻食物');
          notes.add('可适当添加陈皮、茯苓等健脾祛湿食材');
          break;
        case TraditionalChineseBodyType.dryConstitution:
          notes.add('宜食用滋阴润燥食物，避免燥热干性食物');
          notes.add('可适当添加百合、银耳等滋阴润燥食材');
          break;
        default:
          break;
      }
    }
    
    return notes;
  }
  
  /// 添加维生素推荐
  void _addVitaminRecommendations(List<NutrientRecommendation> recommendations) {
    // 添加常见维生素的推荐摄入量
    recommendations.add(NutrientRecommendation(
      name: '维生素A',
      recommendedAmount: 800.0,
      unit: '微克',
      upperLimit: 3000.0,
      foodSources: ['胡萝卜', '红薯', '菠菜', '芒果', '动物肝脏'],
    ));
    
    recommendations.add(NutrientRecommendation(
      name: '维生素B1',
      recommendedAmount: 1.2,
      unit: '毫克',
      foodSources: ['全谷物', '瘦肉', '坚果', '豆类'],
    ));
    
    recommendations.add(NutrientRecommendation(
      name: '维生素B2',
      recommendedAmount: 1.3,
      unit: '毫克',
      foodSources: ['牛奶', '蛋类', '瘦肉', '绿叶蔬菜'],
    ));
    
    recommendations.add(NutrientRecommendation(
      name: '维生素B6',
      recommendedAmount: 1.3,
      unit: '毫克',
      upperLimit: 100.0,
      foodSources: ['禽肉', '鱼', '全谷物', '香蕉'],
    ));
    
    recommendations.add(NutrientRecommendation(
      name: '维生素B12',
      recommendedAmount: 2.4,
      unit: '微克',
      foodSources: ['动物肝脏', '鱼', '蛋类', '奶制品'],
    ));
    
    recommendations.add(NutrientRecommendation(
      name: '维生素C',
      recommendedAmount: 100.0,
      unit: '毫克',
      upperLimit: 2000.0,
      foodSources: ['柑橘类水果', '猕猴桃', '辣椒', '草莓', '西兰花'],
    ));
    
    recommendations.add(NutrientRecommendation(
      name: '维生素D',
      recommendedAmount: 10.0,
      unit: '微克',
      upperLimit: 100.0,
      foodSources: ['阳光照射', '鱼油', '蛋黄', '奶制品'],
    ));
    
    recommendations.add(NutrientRecommendation(
      name: '维生素E',
      recommendedAmount: 15.0,
      unit: '毫克',
      upperLimit: 1000.0,
      foodSources: ['植物油', '坚果', '种子', '全谷物'],
    ));
    
    recommendations.add(NutrientRecommendation(
      name: '叶酸',
      recommendedAmount: 400.0,
      unit: '微克',
      upperLimit: 1000.0,
      foodSources: ['绿叶蔬菜', '豆类', '水果', '全谷物'],
    ));
  }
  
  /// 获取基本推荐
  List<NutrientRecommendation> _getBasicRecommendations() {
    // 提供基本的营养素推荐
    final recommendations = <NutrientRecommendation>[];
    
    // 宏量营养素
    recommendations.add(NutrientRecommendation(
      name: '蛋白质',
      recommendedAmount: 55.0,
      unit: '克',
      foodSources: ['瘦肉', '鱼', '豆腐', '鸡蛋', '酸奶'],
    ));
    
    recommendations.add(NutrientRecommendation(
      name: '碳水化合物',
      recommendedAmount: 250.0,
      unit: '克',
      upperLimit: 300.0,
      foodSources: ['米饭', '面条', '燕麦', '土豆', '水果'],
    ));
    
    recommendations.add(NutrientRecommendation(
      name: '脂肪',
      recommendedAmount: 60.0,
      unit: '克',
      upperLimit: 80.0,
      foodSources: ['橄榄油', '坚果', '鱼油', '牛油果'],
    ));
    
    recommendations.add(NutrientRecommendation(
      name: '纤维素',
      recommendedAmount: 25.0,
      unit: '克',
      foodSources: ['全谷物', '豆类', '水果', '蔬菜'],
    ));
    
    // 微量营养素
    recommendations.add(NutrientRecommendation(
      name: '钙',
      recommendedAmount: 1000.0,
      unit: '毫克',
      upperLimit: 2500.0,
      foodSources: ['牛奶', '酸奶', '奶酪', '豆腐', '小鱼干'],
    ));
    
    recommendations.add(NutrientRecommendation(
      name: '铁',
      recommendedAmount: 18.0,
      unit: '毫克',
      upperLimit: 45.0,
      foodSources: ['红肉', '豆类', '菠菜', '贝类'],
    ));
    
    // 添加维生素
    _addVitaminRecommendations(recommendations);
    
    return recommendations;
  }
  
  /// 生成每日膳食安排
  Future<List<DailyMealSchedule>> _generateMealSchedules(
    String userId,
    DateTime startDate,
    int durationInDays,
    double targetCalories,
    double targetProtein,
    double targetCarbs,
    double targetFat,
    MealPlanType planType,
    DietType dietType,
    DietaryPreference? preference,
    TraditionalChineseBodyType? bodyType,
    List<String>? healthConditions,
  ) async {
    // 这里简化实现，实际应用中需要更复杂的膳食生成算法
    final List<DailyMealSchedule> schedules = [];
    
    for (int i = 0; i < durationInDays; i++) {
      final date = startDate.add(Duration(days: i));
      final seasonalAdjustment = _generateSeasonalAdjustment(_getCurrentSeason(date), bodyType);
      
      // 生成当天的膳食
      final dailySchedule = await generateDailyMealSuggestion(
        userId,
        date: date,
        planType: planType,
      );
      
      schedules.add(dailySchedule);
    }
    
    return schedules;
  }
  
  /// 生成季节性调整建议
  String _generateSeasonalAdjustment(String season, TraditionalChineseBodyType? bodyType) {
    if (bodyType == null) {
      switch (season) {
        case 'spring':
          return '春季饮食宜温补阳气，可多食用葱、香菜等辛温食物，少食酸味食物。';
        case 'summer':
          return '夏季饮食宜清淡，可多食用绿豆、西瓜等清热解暑食物，少食温热食物。';
        case 'autumn':
          return '秋季饮食宜润燥，可多食用梨、银耳等滋阴润肺食物，少食辛辣刺激性食物。';
        case 'winter':
          return '冬季饮食宜温补，可多食用羊肉、姜等温热食物，少食生冷食物。';
        default:
          return '根据季节变化调整饮食结构，选择当季新鲜食材。';
      }
    } else {
      // 根据体质和季节提供更个性化的建议
      // 此处代码省略，实际应用中需要详细实现
      return '根据您的体质特点和当前季节，已为您调整膳食结构。';
    }
  }
  
  /// 生成膳食特别说明
  String _generateSpecialInstructions(DateTime date, TraditionalChineseBodyType? bodyType) {
    // 简化实现，实际应用需要更详细的逻辑
    return '请保持规律饮食，每日饮水1500-2000毫升，细嚼慢咽，避免暴饮暴食。';
  }
  
  /// 生成个性化建议
  Future<List<String>> _generatePersonalizedRecommendations(
    String userId,
    MealPlanType type,
    DietType dietType,
    TraditionalChineseBodyType? bodyType,
    List<String>? healthConditions,
  ) async {
    // 简化实现，实际应用需要更详细的个性化逻辑
    final recommendations = <String>[
      '保持饮食多样化，每天摄入12-15种不同的食物',
      '控制精制糖和盐的摄入量',
      '增加蔬菜和水果的摄入，每天至少5份',
      '选择全谷物而非精制谷物',
      '优先选择健康脂肪来源，如橄榄油、鱼油',
    ];
    
    // 根据计划类型添加建议
    if (type == MealPlanType.weightLoss) {
      recommendations.add('用小碗盘进餐，帮助控制份量');
      recommendations.add('避免深夜进食，晚餐与睡觉间隔至少3小时');
    } else if (type == MealPlanType.muscleGain) {
      recommendations.add('训练后30分钟内补充蛋白质和碳水化合物');
      recommendations.add('每3-4小时进食一次，确保足够的营养摄入');
    }
    
    // 根据体质添加建议
    if (bodyType != null) {
      final bodyTypeRecommendations = await _medicinalFoodAgent.getRecommendationsForBodyType(bodyType);
      recommendations.addAll(bodyTypeRecommendations);
    }
    
    return recommendations;
  }
  
  /// 生成一餐膳食
  Future<Meal> _generateMeal(
    String id,
    String name,
    TimeOfDay timeOfDay,
    double targetCalories,
    double targetProtein,
    double targetCarbs,
    double targetFat,
    DietType dietType,
    TraditionalChineseBodyType? bodyType,
    DietaryPreference? preference,
    List<MedicinalFood> seasonalFoods,
  ) async {
    // 简化实现，实际应用需要更复杂的算法
    // 这里只是创建一个基本结构的膳食对象
    
    // 创建食物项列表
    final foodItems = <MealFoodItem>[];
    
    // 根据饮食类型和体质选择食物
    // 此处是简化逻辑，实际应用中需要更复杂的食物选择算法
    if (dietType == DietType.vegetarian || dietType == DietType.vegan) {
      // 添加植物性食物
      foodItems.add(MealFoodItem(
        name: '豆腐',
        amount: 100,
        unit: '克',
        calories: 80,
        protein: 8,
        carbohydrates: 2,
        fat: 4,
        preparationMethod: '清蒸',
      ));
    } else {
      // 添加肉类
      foodItems.add(MealFoodItem(
        name: '鸡胸肉',
        amount: 100,
        unit: '克',
        calories: 165,
        protein: 31,
        carbohydrates: 0,
        fat: 3.6,
        preparationMethod: '水煮',
      ));
    }
    
    // 添加主食
    foodItems.add(MealFoodItem(
      name: '糙米饭',
      amount: 100,
      unit: '克',
      calories: 111,
      protein: 2.6,
      carbohydrates: 23,
      fat: 0.9,
      preparationMethod: '蒸',
    ));
    
    // 添加蔬菜
    foodItems.add(MealFoodItem(
      name: '西兰花',
      amount: 100,
      unit: '克',
      calories: 34,
      protein: 2.8,
      carbohydrates: 7,
      fat: 0.4,
      preparationMethod: '清炒',
    ));
    
    // 计算总营养值
    double totalCalories = 0;
    double totalProtein = 0;
    double totalCarbs = 0;
    double totalFat = 0;
    
    for (final item in foodItems) {
      totalCalories += item.calories;
      totalProtein += item.protein;
      totalCarbs += item.carbohydrates;
      totalFat += item.fat;
    }
    
    // 创建膳食对象
    return Meal(
      id: id,
      name: name,
      type: name,
      timeOfDay: timeOfDay,
      foodItems: foodItems,
      totalCalories: totalCalories,
      totalProtein: totalProtein,
      totalCarbohydrates: totalCarbs,
      totalFat: totalFat,
      preparationInstructions: '根据个人口味适当调整调料用量，保持清淡为宜。',
    );
  }
  
  /// 创建默认的每日膳食安排
  DailyMealSchedule _createDefaultDailyMealSchedule(DateTime date) {
    // 创建一个基本的默认膳食安排
    final breakfast = Meal(
      id: 'default_breakfast',
      name: '默认早餐',
      type: '早餐',
      timeOfDay: TimeOfDay(hour: 7, minute: 30),
      foodItems: [
        MealFoodItem(
          name: '全麦面包',
          amount: 60,
          unit: '克',
          calories: 160,
          protein: 8,
          carbohydrates: 30,
          fat: 2,
        ),
        MealFoodItem(
          name: '鸡蛋',
          amount: 50,
          unit: '克',
          calories: 80,
          protein: 6,
          carbohydrates: 1,
          fat: 6,
        ),
      ],
      totalCalories: 240,
      totalProtein: 14,
      totalCarbohydrates: 31,
      totalFat: 8,
    );
    
    final lunch = Meal(
      id: 'default_lunch',
      name: '默认午餐',
      type: '午餐',
      timeOfDay: TimeOfDay(hour: 12, minute: 0),
      foodItems: [
        MealFoodItem(
          name: '米饭',
          amount: 100,
          unit: '克',
          calories: 130,
          protein: 2.7,
          carbohydrates: 28,
          fat: 0.3,
        ),
        MealFoodItem(
          name: '炒青菜',
          amount: 100,
          unit: '克',
          calories: 30,
          protein: 2,
          carbohydrates: 5,
          fat: 0.5,
        ),
      ],
      totalCalories: 160,
      totalProtein: 4.7,
      totalCarbohydrates: 33,
      totalFat: 0.8,
    );
    
    final dinner = Meal(
      id: 'default_dinner',
      name: '默认晚餐',
      type: '晚餐',
      timeOfDay: TimeOfDay(hour: 18, minute: 0),
      foodItems: [
        MealFoodItem(
          name: '番薯',
          amount: 150,
          unit: '克',
          calories: 150,
          protein: 2,
          carbohydrates: 35,
          fat: 0.1,
        ),
        MealFoodItem(
          name: '鱼',
          amount: 100,
          unit: '克',
          calories: 100,
          protein: 20,
          carbohydrates: 0,
          fat: 2,
        ),
      ],
      totalCalories: 250,
      totalProtein: 22,
      totalCarbohydrates: 35,
      totalFat: 2.1,
    );
    
    return DailyMealSchedule(
      date: date,
      meals: [breakfast, lunch, dinner],
      totalCalories: 650,
      totalProtein: 40.7,
      totalCarbohydrates: 99,
      totalFat: 10.9,
      specialInstructions: '这是默认膳食安排，请根据个人情况调整。',
    );
  }
}
  
// Provider 定义
final nutritionBalanceAgentProvider = Provider<NutritionBalanceAgent>((ref) {
  final agent = ref.watch(aiAgentProvider('nutrition_balance_agent'));
  final learningSystem = ref.watch(autonomousLearningSystemProvider);
  final ragService = ref.watch(ragServiceProvider);
  final securityFramework = ref.watch(securityPrivacyFrameworkProvider);
  final medicinalFoodAgent = ref.watch(medicinalFoodAgentProvider);
  final knowledgeGraphAgent = ref.watch(knowledgeGraphAgentProvider);
  
  return NutritionBalanceAgentImpl(
    agent: agent,
    learningSystem: learningSystem,
    ragService: ragService,
    securityFramework: securityFramework,
    medicinalFoodAgent: medicinalFoodAgent,
    knowledgeGraphAgent: knowledgeGraphAgent,
  );
});

// 营养平衡代理的状态管理
final nutritionBalanceAgentStateProvider = StateProvider<Map<String, dynamic>>((ref) {
  return {
    'isInitialized': false,
    'activeUserMealPlans': <String, MealPlan>{},
    'nutritionSummaries': <String, NutritionSummary>{},
  };
});

// 用户的膳食计划提供者
final userMealPlansProvider = FutureProvider.family<List<MealPlan>, String>((ref, userId) async {
  final nutritionAgent = ref.watch(nutritionBalanceAgentProvider);
  return await nutritionAgent.getUserMealPlans(userId);
});

// 用户的营养摘要提供者
final nutritionSummaryProvider = FutureProvider.family<NutritionSummary?, Map<String, dynamic>>((ref, params) async {
  final userId = params['userId'] as String;
  final startDate = params['startDate'] as DateTime;
  final endDate = params['endDate'] as DateTime;
  
  final nutritionAgent = ref.watch(nutritionBalanceAgentProvider);
  try {
    return await nutritionAgent.createNutritionSummary(
      userId,
      startDate: startDate,
      endDate: endDate,
    );
  } catch (e) {
    if (kDebugMode) {
      print('获取营养摘要失败: $e');
    }
    return null;
  }
});

// 每日膳食建议提供者
final dailyMealSuggestionProvider = FutureProvider.family<DailyMealSchedule, Map<String, dynamic>>((ref, params) async {
  final userId = params['userId'] as String;
  final date = params['date'] as DateTime?;
  final planType = params['planType'] as MealPlanType?;
  
  final nutritionAgent = ref.watch(nutritionBalanceAgentProvider);
  return await nutritionAgent.generateDailyMealSuggestion(
    userId,
    date: date,
    planType: planType,
  );
});
  