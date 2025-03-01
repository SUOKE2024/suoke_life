import 'dart:async';
import 'dart:convert';

import 'package:flutter/foundation.dart';

import '../models/ai_agent.dart';
import '../core/agent_microkernel.dart';
import '../core/autonomous_learning_system.dart';
import '../expert/knowledge_graph_agent.dart';
import '../expert/health_management_agent.dart';
import '../integration/service_integration.dart';
import '../core/security_privacy_framework.dart';

/// 食材属性（中医四性）
enum FoodProperty {
  /// 寒性
  cold,
  
  /// 凉性
  cool,
  
  /// 平性
  neutral,
  
  /// 温性
  warm,
  
  /// 热性
  hot,
}

/// 食材味道（中医五味）
enum FoodFlavor {
  /// 酸味
  sour,
  
  /// 苦味
  bitter,
  
  /// 甘味（甜）
  sweet,
  
  /// 辛味（辣）
  pungent,
  
  /// 咸味
  salty,
}

/// 食材功效分类
enum FoodTherapeuticEffect {
  /// 补气
  tonifyQi,
  
  /// 养血
  nourishBlood,
  
  /// 补阴
  tonifyYin,
  
  /// 补阳
  tonifyYang,
  
  /// 祛风
  dispelWind,
  
  /// 清热
  clearHeat,
  
  /// 祛湿
  removeDampness,
  
  /// 化痰
  resolvePhlegm,
  
  /// 理气
  regulateQi,
  
  /// 活血
  activateBlood,
  
  /// 消食
  digestFood,
  
  /// 安神
  calmMind,
  
  /// 明目
  benefitEyes,
  
  /// 润肺
  moistenLungs,
  
  /// 健脾
  strengthenSpleen,
  
  /// 补肾
  tonifyKidney,
  
  /// 护肝
  protectLiver,
  
  /// 益智
  enhanceBrain,
}

/// 中医体质分类
enum TraditionalChineseBodyType {
  /// 平和质
  balanced,
  
  /// 气虚质
  qiDeficiency,
  
  /// 阳虚质
  yangDeficiency,
  
  /// 阴虚质
  yinDeficiency,
  
  /// 痰湿质
  phlegmDampness,
  
  /// 湿热质
  dampnessHeat,
  
  /// 血瘀质
  bloodStasis,
  
  /// 气郁质
  qiStagnation,
  
  /// 特禀质
  allergic,
}

/// 处方类型
enum PrescriptionType {
  /// 药膳
  medicinalFood,
  
  /// 食疗
  dietTherapy,
  
  /// 药茶
  medicinalTea,
  
  /// 药酒
  medicinalWine,
  
  /// 药粥
  medicinalPorridge,
  
  /// 药汤
  medicinalSoup,
}

/// 膳食时段
enum MealTime {
  /// 早餐
  breakfast,
  
  /// 午餐
  lunch,
  
  /// 晚餐
  dinner,
  
  /// 加餐
  snack,
}

/// 药食同源食材
class MedicinalFood {
  /// 食材ID
  final String id;
  
  /// 中文名称
  final String chineseName;
  
  /// 英文名称
  final String? englishName;
  
  /// 拼音
  final String? pinyin;
  
  /// 别名列表
  final List<String>? aliases;
  
  /// 食材分类
  final List<String> categories;
  
  /// 食材属性（四性）
  final FoodProperty property;
  
  /// 食材味道（五味）
  final List<FoodFlavor> flavors;
  
  /// 归经
  final List<String> meridians;
  
  /// 功效列表
  final List<FoodTherapeuticEffect> effects;
  
  /// 功效描述
  final String efficacyDescription;
  
  /// 宜用人群
  final List<String> suitableFor;
  
  /// 禁忌人群
  final List<String> contraindicatedFor;
  
  /// 用法用量
  final String? usageGuideline;
  
  /// 现代研究
  final String? modernResearch;
  
  /// 常用搭配
  final List<String>? commonCombinations;
  
  /// 相关方剂
  final List<String>? relatedPrescriptions;
  
  /// 图片URL列表
  final List<String>? imageUrls;
  
  /// 食材来源
  final String? source;
  
  /// 价格（人民币，元/kg）
  final double? price;
  
  /// 营养成分
  final Map<String, dynamic>? nutrition;
  
  /// 相关文献引用
  final List<String>? references;

  const MedicinalFood({
    required this.id,
    required this.chineseName,
    this.englishName,
    this.pinyin,
    this.aliases,
    required this.categories,
    required this.property,
    required this.flavors,
    required this.meridians,
    required this.effects,
    required this.efficacyDescription,
    required this.suitableFor,
    required this.contraindicatedFor,
    this.usageGuideline,
    this.modernResearch,
    this.commonCombinations,
    this.relatedPrescriptions,
    this.imageUrls,
    this.source,
    this.price,
    this.nutrition,
    this.references,
  });
  
  /// 从JSON创建
  factory MedicinalFood.fromJson(Map<String, dynamic> json) {
    return MedicinalFood(
      id: json['id'],
      chineseName: json['chinese_name'],
      englishName: json['english_name'],
      pinyin: json['pinyin'],
      aliases: json['aliases'] != null 
        ? List<String>.from(json['aliases']) 
        : null,
      categories: List<String>.from(json['categories']),
      property: FoodProperty.values.firstWhere(
        (p) => p.toString() == 'FoodProperty.${json['property']}',
        orElse: () => FoodProperty.neutral,
      ),
      flavors: (json['flavors'] as List).map((f) => 
        FoodFlavor.values.firstWhere(
          (fl) => fl.toString() == 'FoodFlavor.$f',
          orElse: () => FoodFlavor.sweet,
        )
      ).toList(),
      meridians: List<String>.from(json['meridians']),
      effects: (json['effects'] as List).map((e) => 
        FoodTherapeuticEffect.values.firstWhere(
          (ef) => ef.toString() == 'FoodTherapeuticEffect.$e',
          orElse: () => FoodTherapeuticEffect.tonifyQi,
        )
      ).toList(),
      efficacyDescription: json['efficacy_description'],
      suitableFor: List<String>.from(json['suitable_for']),
      contraindicatedFor: List<String>.from(json['contraindicated_for']),
      usageGuideline: json['usage_guideline'],
      modernResearch: json['modern_research'],
      commonCombinations: json['common_combinations'] != null 
        ? List<String>.from(json['common_combinations']) 
        : null,
      relatedPrescriptions: json['related_prescriptions'] != null 
        ? List<String>.from(json['related_prescriptions']) 
        : null,
      imageUrls: json['image_urls'] != null 
        ? List<String>.from(json['image_urls']) 
        : null,
      source: json['source'],
      price: json['price']?.toDouble(),
      nutrition: json['nutrition'],
      references: json['references'] != null 
        ? List<String>.from(json['references']) 
        : null,
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'chinese_name': chineseName,
      'english_name': englishName,
      'pinyin': pinyin,
      'aliases': aliases,
      'categories': categories,
      'property': property.toString().split('.').last,
      'flavors': flavors.map((f) => f.toString().split('.').last).toList(),
      'meridians': meridians,
      'effects': effects.map((e) => e.toString().split('.').last).toList(),
      'efficacy_description': efficacyDescription,
      'suitable_for': suitableFor,
      'contraindicated_for': contraindicatedFor,
      'usage_guideline': usageGuideline,
      'modern_research': modernResearch,
      'common_combinations': commonCombinations,
      'related_prescriptions': relatedPrescriptions,
      'image_urls': imageUrls,
      'source': source,
      'price': price,
      'nutrition': nutrition,
      'references': references,
    };
  }
}

/// 药膳配方
class MedicinalRecipe {
  /// 配方ID
  final String id;
  
  /// 配方名称
  final String name;
  
  /// 处方类型
  final PrescriptionType type;
  
  /// 配方食材列表
  final List<RecipeIngredient> ingredients;
  
  /// 制作方法
  final String preparation;
  
  /// 食用方法
  final String? consumptionMethod;
  
  /// 推荐食用时间
  final List<MealTime>? recommendedMealTimes;
  
  /// 功效描述
  final String efficacyDescription;
  
  /// 主治
  final List<String> mainIndications;
  
  /// 宜用人群
  final List<String> suitableFor;
  
  /// 禁忌人群
  final List<String> contraindicatedFor;
  
  /// 相关中医理论
  final String? tcmTheoryBackground;
  
  /// 图片URL列表
  final List<String>? imageUrls;
  
  /// 视频URL
  final String? videoUrl;
  
  /// 适用体质
  final List<TraditionalChineseBodyType>? suitableBodyTypes;
  
  /// 来源/出处
  final String? source;
  
  /// 难度级别（1-5）
  final int? difficultyLevel;
  
  /// 准备时间（分钟）
  final int? prepTime;
  
  /// 烹饪时间（分钟）
  final int? cookTime;
  
  /// 评分（1-5）
  final double? rating;
  
  /// 评论数
  final int? reviewCount;
  
  /// 相关文献引用
  final List<String>? references;

  const MedicinalRecipe({
    required this.id,
    required this.name,
    required this.type,
    required this.ingredients,
    required this.preparation,
    this.consumptionMethod,
    this.recommendedMealTimes,
    required this.efficacyDescription,
    required this.mainIndications,
    required this.suitableFor,
    required this.contraindicatedFor,
    this.tcmTheoryBackground,
    this.imageUrls,
    this.videoUrl,
    this.suitableBodyTypes,
    this.source,
    this.difficultyLevel,
    this.prepTime,
    this.cookTime,
    this.rating,
    this.reviewCount,
    this.references,
  });
  
  /// 从JSON创建
  factory MedicinalRecipe.fromJson(Map<String, dynamic> json) {
    return MedicinalRecipe(
      id: json['id'],
      name: json['name'],
      type: PrescriptionType.values.firstWhere(
        (t) => t.toString() == 'PrescriptionType.${json['type']}',
        orElse: () => PrescriptionType.medicinalFood,
      ),
      ingredients: (json['ingredients'] as List).map(
        (i) => RecipeIngredient.fromJson(i)
      ).toList(),
      preparation: json['preparation'],
      consumptionMethod: json['consumption_method'],
      recommendedMealTimes: json['recommended_meal_times'] != null 
        ? (json['recommended_meal_times'] as List).map((m) => 
            MealTime.values.firstWhere(
              (mt) => mt.toString() == 'MealTime.$m',
              orElse: () => MealTime.lunch,
            )
          ).toList() 
        : null,
      efficacyDescription: json['efficacy_description'],
      mainIndications: List<String>.from(json['main_indications']),
      suitableFor: List<String>.from(json['suitable_for']),
      contraindicatedFor: List<String>.from(json['contraindicated_for']),
      tcmTheoryBackground: json['tcm_theory_background'],
      imageUrls: json['image_urls'] != null 
        ? List<String>.from(json['image_urls']) 
        : null,
      videoUrl: json['video_url'],
      suitableBodyTypes: json['suitable_body_types'] != null 
        ? (json['suitable_body_types'] as List).map((b) => 
            TraditionalChineseBodyType.values.firstWhere(
              (bt) => bt.toString() == 'TraditionalChineseBodyType.$b',
              orElse: () => TraditionalChineseBodyType.balanced,
            )
          ).toList() 
        : null,
      source: json['source'],
      difficultyLevel: json['difficulty_level'],
      prepTime: json['prep_time'],
      cookTime: json['cook_time'],
      rating: json['rating']?.toDouble(),
      reviewCount: json['review_count'],
      references: json['references'] != null 
        ? List<String>.from(json['references']) 
        : null,
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'type': type.toString().split('.').last,
      'ingredients': ingredients.map((i) => i.toJson()).toList(),
      'preparation': preparation,
      'consumption_method': consumptionMethod,
      'recommended_meal_times': recommendedMealTimes?.map(
        (m) => m.toString().split('.').last
      ).toList(),
      'efficacy_description': efficacyDescription,
      'main_indications': mainIndications,
      'suitable_for': suitableFor,
      'contraindicated_for': contraindicatedFor,
      'tcm_theory_background': tcmTheoryBackground,
      'image_urls': imageUrls,
      'video_url': videoUrl,
      'suitable_body_types': suitableBodyTypes?.map(
        (b) => b.toString().split('.').last
      ).toList(),
      'source': source,
      'difficulty_level': difficultyLevel,
      'prep_time': prepTime,
      'cook_time': cookTime,
      'rating': rating,
      'review_count': reviewCount,
      'references': references,
    };
  }
}

/// 配方食材
class RecipeIngredient {
  /// 食材ID
  final String foodId;
  
  /// 食材名称
  final String name;
  
  /// 用量
  final String amount;
  
  /// 药用部位
  final String? medicinalPart;
  
  /// 处理方法
  final String? processingMethod;
  
  /// 是否必需
  final bool isRequired;
  
  /// 在配方中的功效
  final String? roleInRecipe;
  
  const RecipeIngredient({
    required this.foodId,
    required this.name,
    required this.amount,
    this.medicinalPart,
    this.processingMethod,
    this.isRequired = true,
    this.roleInRecipe,
  });
  
  /// 从JSON创建
  factory RecipeIngredient.fromJson(Map<String, dynamic> json) {
    return RecipeIngredient(
      foodId: json['food_id'],
      name: json['name'],
      amount: json['amount'],
      medicinalPart: json['medicinal_part'],
      processingMethod: json['processing_method'],
      isRequired: json['is_required'] ?? true,
      roleInRecipe: json['role_in_recipe'],
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'food_id': foodId,
      'name': name,
      'amount': amount,
      'medicinal_part': medicinalPart,
      'processing_method': processingMethod,
      'is_required': isRequired,
      'role_in_recipe': roleInRecipe,
    };
  }
}

/// 食材搜索过滤条件
class MedicinalFoodFilter {
  /// 关键词
  final String? keyword;
  
  /// 功效列表
  final List<FoodTherapeuticEffect>? effects;
  
  /// 食材属性
  final List<FoodProperty>? properties;
  
  /// 食材味道
  final List<FoodFlavor>? flavors;
  
  /// 归经
  final List<String>? meridians;
  
  /// 适用体质
  final List<TraditionalChineseBodyType>? suitableBodyTypes;
  
  /// 健康状况关键词
  final List<String>? healthConditions;
  
  /// 分类
  final List<String>? categories;
  
  /// 价格范围
  final RangeValues? priceRange;
  
  const MedicinalFoodFilter({
    this.keyword,
    this.effects,
    this.properties,
    this.flavors,
    this.meridians,
    this.suitableBodyTypes,
    this.healthConditions,
    this.categories,
    this.priceRange,
  });
}

/// 价格范围
class RangeValues {
  final double start;
  final double end;
  
  const RangeValues(this.start, this.end);
}

/// 食疗方案
class DietTherapyPlan {
  /// 方案ID
  final String id;
  
  /// 方案名称
  final String name;
  
  /// 方案描述
  final String description;
  
  /// 目标健康状况
  final List<String> targetHealthConditions;
  
  /// 适用体质
  final List<TraditionalChineseBodyType> suitableBodyTypes;
  
  /// 推荐食材列表
  final List<MedicinalFood> recommendedFoods;
  
  /// 避免食材列表
  final List<MedicinalFood> avoidFoods;
  
  /// 推荐配方列表
  final List<MedicinalRecipe> recommendedRecipes;
  
  /// 每周食谱安排
  final Map<String, List<MedicinalRecipe>>? weeklyMealPlan;
  
  /// 中医理论依据
  final String tcmTheoryBasis;
  
  /// 注意事项
  final List<String> precautions;
  
  /// 预期效果
  final String expectedOutcomes;
  
  /// 方案周期（天）
  final int durationDays;
  
  /// 创建时间
  final DateTime createdAt;
  
  /// 更新时间
  final DateTime updatedAt;
  
  /// 创建者
  final String createdBy;
  
  const DietTherapyPlan({
    required this.id,
    required this.name,
    required this.description,
    required this.targetHealthConditions,
    required this.suitableBodyTypes,
    required this.recommendedFoods,
    required this.avoidFoods,
    required this.recommendedRecipes,
    this.weeklyMealPlan,
    required this.tcmTheoryBasis,
    required this.precautions,
    required this.expectedOutcomes,
    required this.durationDays,
    required this.createdAt,
    required this.updatedAt,
    required this.createdBy,
  });
}

/// 食材分析结果
class FoodAnalysisResult {
  /// 食材
  final MedicinalFood food;
  
  /// 适合当前用户体质的评分（0-100）
  final int bodyTypeCompatibilityScore;
  
  /// 适合当前季节的评分（0-100）
  final int seasonalCompatibilityScore;
  
  /// 适合当前健康状况的评分（0-100）
  final int healthConditionCompatibilityScore;
  
  /// 总体推荐度（0-100）
  final int overallRecommendationScore;
  
  /// 推荐理由
  final List<String> recommendationReasons;
  
  /// 注意事项
  final List<String>? precautions;
  
  /// 建议用法
  final String? suggestedUsage;
  
  /// 推荐搭配
  final List<MedicinalFood>? recommendedCombinations;
  
  const FoodAnalysisResult({
    required this.food,
    required this.bodyTypeCompatibilityScore,
    required this.seasonalCompatibilityScore,
    required this.healthConditionCompatibilityScore,
    required this.overallRecommendationScore,
    required this.recommendationReasons,
    this.precautions,
    this.suggestedUsage,
    this.recommendedCombinations,
  });
}

/// 药食同源代理接口
abstract class MedicinalFoodAgent {
  /// 根据条件搜索药食同源食材
  Future<List<MedicinalFood>> searchMedicinalFoods(MedicinalFoodFilter filter);
  
  /// 获取食材详情
  Future<MedicinalFood?> getFoodDetail(String foodId);
  
  /// 根据健康状况获取推荐食材
  Future<List<FoodAnalysisResult>> getRecommendedFoodsForHealthConditions(
    List<String> healthConditions, {
    TraditionalChineseBodyType? bodyType,
    String? userId,
  });
  
  /// 根据体质获取推荐食材
  Future<List<MedicinalFood>> getRecommendedFoodsForBodyType(
    TraditionalChineseBodyType bodyType,
  );
  
  /// 搜索药膳配方
  Future<List<MedicinalRecipe>> searchRecipes({
    String? keyword,
    List<String>? healthConditions,
    List<FoodTherapeuticEffect>? effects,
    PrescriptionType? type,
    TraditionalChineseBodyType? bodyType,
  });
  
  /// 获取配方详情
  Future<MedicinalRecipe?> getRecipeDetail(String recipeId);
  
  /// 创建个性化食疗方案
  Future<DietTherapyPlan> createPersonalizedDietPlan({
    required String userId,
    required List<String> healthConditions,
    required TraditionalChineseBodyType bodyType,
    int durationDays = 28,
  });
  
  /// 分析食材的药用价值
  Future<FoodAnalysisResult> analyzeFoodMedicinalValue(
    String foodId, {
    String? userId,
    List<String>? userHealthConditions,
    TraditionalChineseBodyType? userBodyType,
  });
  
  /// 获取季节性养生食材
  Future<List<MedicinalFood>> getSeasonalHealthFoods();
  
  /// 获取针对特定脏腑的食材
  Future<List<MedicinalFood>> getFoodsForOrgan(String organName);
  
  /// 获取相互作用（食材相克）信息
  Future<List<Map<String, dynamic>>> getFoodInteractions(List<String> foodIds);
  
  /// 获取常见体质调理方案
  Future<Map<TraditionalChineseBodyType, List<String>>> getBodyTypeAdjustmentGuidelines();
}

/// 药食同源代理实现
class MedicinalFoodAgentImpl implements MedicinalFoodAgent {
  final AIAgent _aiAgent;
  final ServiceIntegration _serviceIntegration;
  final AgentMicrokernel _microkernel;
  final SecurityPrivacyFramework _securityFramework;
  final KnowledgeGraphAgent? _knowledgeGraphAgent;
  final HealthManagementAgent? _healthManagementAgent;
  final AutonomousLearningSystem _learningSystem;
  
  MedicinalFoodAgentImpl({
    required AIAgent aiAgent,
    required ServiceIntegration serviceIntegration,
    required AgentMicrokernel microkernel,
    required SecurityPrivacyFramework securityFramework,
    required AutonomousLearningSystem learningSystem,
    this.knowledgeGraphAgentId,
    this.healthManagementAgentId,
  }) : _aiAgent = aiAgent,
       _serviceIntegration = serviceIntegration,
       _microkernel = microkernel,
       _securityFramework = securityFramework,
       _learningSystem = learningSystem,
       _knowledgeGraphAgent = null,
       _healthManagementAgent = null;
  
  /// 知识图谱代理ID（可选）
  final String? knowledgeGraphAgentId;
  
  /// 健康管理代理ID（可选）
  final String? healthManagementAgentId;
  
  /// 初始化
  Future<void> initialize() async {
    // 注册接收消息的处理函数
    _microkernel.registerAgent(_aiAgent.id, _handleMessage);
    
    // 如果提供了知识图谱代理ID，建立通信
    if (knowledgeGraphAgentId != null) {
      final initMessage = AgentMessage(
        senderId: _aiAgent.id,
        receiverId: knowledgeGraphAgentId!,
        type: AgentMessageType.query,
        content: {
          'action': 'register_callback',
          'callback_agent_id': _aiAgent.id,
        },
      );
      
      await _microkernel.sendMessage(initMessage);
    }
    
    // 如果提供了健康管理代理ID，建立通信
    if (healthManagementAgentId != null) {
      final initMessage = AgentMessage(
        senderId: _aiAgent.id,
        receiverId: healthManagementAgentId!,
        type: AgentMessageType.query,
        content: {
          'action': 'register_callback',
          'callback_agent_id': _aiAgent.id,
        },
      );
      
      await _microkernel.sendMessage(initMessage);
    }
  }
  
  /// 处理接收到的消息
  Future<void> _handleMessage(AgentMessage message) async {
    try {
      final action = message.content['action'] as String?;
      
      if (action == null) {
        return;
      }
      
      switch (action) {
        case 'health_update':
          final healthData = message.content['health_data'];
          if (healthData != null) {
            // 处理健康数据更新
            _processHealthUpdate(healthData);
          }
          break;
          
        case 'knowledge_update':
          final knowledgeData = message.content['knowledge_data'];
          if (knowledgeData != null) {
            // 处理知识图谱更新
            _processKnowledgeUpdate(knowledgeData);
          }
          break;
          
        default:
          // 无法识别的动作
          break;
      }
      
      // 如果消息需要响应，发送响应
      if (message.requiresResponse) {
        final responseMessage = message.createResponse(
          responderId: _aiAgent.id,
          responseContent: {
            'success': true,
            'message': 'Message processed successfully',
          },
        );
        
        await _microkernel.sendMessage(responseMessage);
      }
      
    } catch (e) {
      print('Error handling message: $e');
      
      // 如果消息需要响应，发送错误响应
      if (message.requiresResponse) {
        final errorResponse = message.createResponse(
          responderId: _aiAgent.id,
          responseContent: {
            'success': false,
            'error': e.toString(),
          },
        );
        
        await _microkernel.sendMessage(errorResponse);
      }
    }
  }
  
  /// 处理健康数据更新
  void _processHealthUpdate(Map<String, dynamic> healthData) {
    // 实现健康数据更新的处理逻辑
    // 例如缓存用户的健康状况，以便在推荐药食同源食材时使用
  }
  
  /// 处理知识图谱更新
  void _processKnowledgeUpdate(Map<String, dynamic> knowledgeData) {
    // 实现知识图谱更新的处理逻辑
    // 例如更新食材之间的关系、功效等信息
  }
  
  @override
  Future<List<MedicinalFood>> searchMedicinalFoods(MedicinalFoodFilter filter) async {
    try {
      // 构建查询参数
      final queryParams = <String, dynamic>{};
      
      if (filter.keyword != null) {
        queryParams['keyword'] = filter.keyword;
      }
      
      if (filter.effects != null && filter.effects!.isNotEmpty) {
        queryParams['effects'] = filter.effects!.map(
          (e) => e.toString().split('.').last
        ).join(',');
      }
      
      if (filter.properties != null && filter.properties!.isNotEmpty) {
        queryParams['properties'] = filter.properties!.map(
          (p) => p.toString().split('.').last
        ).join(',');
      }
      
      if (filter.flavors != null && filter.flavors!.isNotEmpty) {
        queryParams['flavors'] = filter.flavors!.map(
          (f) => f.toString().split('.').last
        ).join(',');
      }
      
      if (filter.meridians != null && filter.meridians!.isNotEmpty) {
        queryParams['meridians'] = filter.meridians!.join(',');
      }
      
      if (filter.suitableBodyTypes != null && filter.suitableBodyTypes!.isNotEmpty) {
        queryParams['suitable_body_types'] = filter.suitableBodyTypes!.map(
          (b) => b.toString().split('.').last
        ).join(',');
      }
      
      if (filter.healthConditions != null && filter.healthConditions!.isNotEmpty) {
        queryParams['health_conditions'] = filter.healthConditions!.join(',');
      }
      
      if (filter.categories != null && filter.categories!.isNotEmpty) {
        queryParams['categories'] = filter.categories!.join(',');
      }
      
      if (filter.priceRange != null) {
        queryParams['min_price'] = filter.priceRange!.start;
        queryParams['max_price'] = filter.priceRange!.end;
      }
      
      // 发送请求到服务
      final response = await _serviceIntegration.sendRequest<Map<String, dynamic>>(
        endpoint: '/api/medicinal-foods/search',
        method: 'GET',
        queryParams: queryParams,
      );
      
      if (!response.success || response.data == null) {
        return [];
      }
      
      final foodsData = response.data!['foods'] as List<dynamic>;
      final foods = foodsData.map(
        (data) => MedicinalFood.fromJson(data as Map<String, dynamic>)
      ).toList();
      
      // 收集学习数据
      await _learningSystem.collectData(LearningDataItem(
        id: 'search_${DateTime.now().millisecondsSinceEpoch}',
        type: LearningDataType.userInteraction,
        source: LearningDataSource.medicinalFoodAgent,
        content: {
          'action': 'search_foods',
          'filter': queryParams,
          'results_count': foods.length,
        },
        timestamp: DateTime.now(),
      ));
      
      return foods;
    } catch (e) {
      print('Error searching medicinal foods: $e');
      return [];
    }
  }
  
  @override
  Future<MedicinalFood?> getFoodDetail(String foodId) async {
    try {
      // 首先尝试从知识图谱获取更丰富的数据
      if (knowledgeGraphAgentId != null) {
        final graphQueryMessage = AgentMessage(
          senderId: _aiAgent.id,
          receiverId: knowledgeGraphAgentId!,
          type: AgentMessageType.query,
          content: {
            'action': 'get_node_details',
            'node_id': foodId,
            'node_type': 'medicinal_food',
          },
          requiresResponse: true,
        );
        
        final messageId = await _microkernel.sendMessage(graphQueryMessage);
        
        // 等待响应，实际实现中应该使用异步回调机制
        // 这里简化处理
        await Future.delayed(const Duration(milliseconds: 500));
        
        // 获取响应消息
        final responses = _microkernel.getAgentMessageHistory(
          agentId: _aiAgent.id,
          type: AgentMessageType.response,
        ).where((msg) => msg.parentMessageId == messageId).toList();
        
        if (responses.isNotEmpty && responses.first.content['success'] == true) {
          final nodeData = responses.first.content['node_data'];
          if (nodeData != null) {
            return MedicinalFood.fromJson(nodeData);
          }
        }
      }
      
      // 如果从知识图谱未获取到，则从API获取
      final response = await _serviceIntegration.sendRequest<Map<String, dynamic>>(
        endpoint: '/api/medicinal-foods/$foodId',
        method: 'GET',
      );
      
      if (!response.success || response.data == null) {
        return null;
      }
      
      return MedicinalFood.fromJson(response.data!);
    } catch (e) {
      print('Error getting food detail: $e');
      return null;
    }
  }
  
  @override
  Future<List<FoodAnalysisResult>> getRecommendedFoodsForHealthConditions(
    List<String> healthConditions, {
    TraditionalChineseBodyType? bodyType,
    String? userId,
  }) async {
    try {
      // 构建查询参数
      final queryParams = <String, dynamic>{
        'health_conditions': healthConditions.join(','),
      };
      
      if (bodyType != null) {
        queryParams['body_type'] = bodyType.toString().split('.').last;
      }
      
      if (userId != null) {
        queryParams['user_id'] = userId;
        
        // 如果有健康管理代理，获取用户的更多健康数据
        if (healthManagementAgentId != null) {
          final healthDataMessage = AgentMessage(
            senderId: _aiAgent.id,
            receiverId: healthManagementAgentId!,
            type: AgentMessageType.query,
            content: {
              'action': 'get_user_health_data',
              'user_id': userId,
            },
            requiresResponse: true,
          );
          
          final messageId = await _microkernel.sendMessage(healthDataMessage);
          
          // 等待响应，实际实现中应该使用异步回调机制
          await Future.delayed(const Duration(milliseconds: 500));
          
          // 获取响应消息
          final responses = _microkernel.getAgentMessageHistory(
            agentId: _aiAgent.id,
            type: AgentMessageType.response,
          ).where((msg) => msg.parentMessageId == messageId).toList();
          
          if (responses.isNotEmpty && responses.first.content['success'] == true) {
            final userData = responses.first.content['data'];
            // 使用用户健康数据补充查询参数
            if (userData != null && userData is Map<String, dynamic>) {
              queryParams.addAll(userData);
            }
          }
        }
      }
      
      // 发送请求到服务
      final response = await _serviceIntegration.sendRequest<Map<String, dynamic>>(
        endpoint: '/api/medicinal-foods/recommend',
        method: 'GET',
        queryParams: queryParams,
      );
      
      if (!response.success || response.data == null) {
        return [];
      }
      
      final foodsData = response.data!['foods'] as List<dynamic>;
      final foods = foodsData.map(
        (data) => FoodAnalysisResult(
          food: MedicinalFood.fromJson(data as Map<String, dynamic>),
          bodyTypeCompatibilityScore: 0,
          seasonalCompatibilityScore: 0,
          healthConditionCompatibilityScore: 0,
          overallRecommendationScore: 0,
          recommendationReasons: [],
          precautions: null,
          suggestedUsage: null,
          recommendedCombinations: null,
        )
      ).toList();
      
      // 收集学习数据
      await _learningSystem.collectData(LearningDataItem(
        id: 'recommend_${DateTime.now().millisecondsSinceEpoch}',
        type: LearningDataType.userInteraction,
        source: LearningDataSource.medicinalFoodAgent,
        content: {
          'action': 'recommend_foods',
          'filter': queryParams,
          'results_count': foods.length,
        },
        timestamp: DateTime.now(),
      ));
      
      return foods;
    } catch (e) {
      print('Error recommending foods: $e');
      return [];
    }
  }
  
  @override
  Future<List<MedicinalFood>> getRecommendedFoodsForBodyType(
    TraditionalChineseBodyType bodyType,
  ) async {
    // Implementation needed
    throw UnimplementedError();
  }
  
  @override
  Future<List<MedicinalRecipe>> searchRecipes({
    String? keyword,
    List<String>? healthConditions,
    List<FoodTherapeuticEffect>? effects,
    PrescriptionType? type,
    TraditionalChineseBodyType? bodyType,
  }) async {
    // Implementation needed
    throw UnimplementedError();
  }
  
  @override
  Future<MedicinalRecipe?> getRecipeDetail(String recipeId) async {
    // Implementation needed
    throw UnimplementedError();
  }
  
  @override
  Future<DietTherapyPlan> createPersonalizedDietPlan({
    required String userId,
    required List<String> healthConditions,
    required TraditionalChineseBodyType bodyType,
    int durationDays = 28,
  }) async {
    // Implementation needed
    throw UnimplementedError();
  }
  
  @override
  Future<FoodAnalysisResult> analyzeFoodMedicinalValue(
    String foodId, {
    String? userId,
    List<String>? userHealthConditions,
    TraditionalChineseBodyType? userBodyType,
  }) async {
    // Implementation needed
    throw UnimplementedError();
  }
  
  @override
  Future<List<MedicinalFood>> getSeasonalHealthFoods() async {
    // Implementation needed
    throw UnimplementedError();
  }
  
  @override
  Future<List<MedicinalFood>> getFoodsForOrgan(String organName) async {
    // Implementation needed
    throw UnimplementedError();
  }
  
  @override
  Future<List<Map<String, dynamic>>> getFoodInteractions(List<String> foodIds) async {
    // Implementation needed
    throw UnimplementedError();
  }
  
  @override
  Future<Map<TraditionalChineseBodyType, List<String>>> getBodyTypeAdjustmentGuidelines() async {
    // Implementation needed
    throw UnimplementedError();
  }
}

/// 默认药食同源代理实现
class DefaultMedicinalFoodAgent implements MedicinalFoodAgent {
  final AgentMicrokernel _microkernel;
  final AutonomousLearningSystem _learningSystem;
  
  /// 构造函数
  DefaultMedicinalFoodAgent(this._microkernel, this._learningSystem);
  
  @override
  AIAgent get agent => AIAgent(
        id: 'medicinal_food_agent',
        name: '药食同源代理',
        type: AIAgentType.supplyChain,
        specialties: ['药膳', '食疗', '药材', '功能食品'],
        description: '专注于中医药膳配方、食疗方案和药食同源知识的AI代理',
        capabilities: [
          AIAgentCapability.knowledgeRetrieval,
          AIAgentCapability.recommendation,
          AIAgentCapability.planning,
        ],
        color: const Color(0xFFE57373),
      );
  
  @override
  Future<List<FoodIngredient>> recommendIngredients({
    required List<String> targetEffects,
    TraditionalChineseBodyType? bodyType,
    List<String>? healthConditions,
    List<String>? dietaryRestrictions,
  }) async {
    // 简化实现 - 实际项目中应通过知识图谱检索和推理
    return [];
  }
  
  @override
  Future<List<MedicinalFoodRecipe>> generateRecipes({
    required List<String> targetEffects,
    List<String>? preferredIngredients,
    TraditionalChineseBodyType? bodyType,
    List<String>? healthConditions,
    List<String>? dietaryRestrictions,
    PrescriptionType prescriptionType = PrescriptionType.medicinalFood,
  }) async {
    // 简化实现 - 实际项目中应使用更复杂的生成逻辑
    return [];
  }
  
  @override
  Future<MedicinalFoodEvaluation> evaluateRecipe(MedicinalFoodRecipe recipe) async {
    // 简化实现
    return MedicinalFoodEvaluation(
      recipe: recipe,
      effectivenessScore: 0.0,
      safetyScore: 0.0,
      balanceScore: 0.0,
      comments: [],
      warning: null,
    );
  }
  
  @override
  Future<List<FoodIngredient>> getIngredientsByProperty(FoodProperty property) async {
    // 简化实现
    return [];
  }
  
  @override
  Future<List<FoodIngredient>> getIngredientsByTaste(FoodTaste taste) async {
    // 简化实现
    return [];
  }
  
  @override
  Future<List<FoodIngredient>> getIngredientsByMeridian(BodyMeridian meridian) async {
    // 简化实现
    return [];
  }
  
  @override
  Future<List<FoodIngredient>> getIngredientsByEffect(MedicinalEffect effect) async {
    // 简化实现
    return [];
  }
  
  @override
  Future<List<FoodIngredient>> searchIngredients(String query) async {
    // 简化实现
    return [];
  }
}
  