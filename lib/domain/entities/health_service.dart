import 'package:equatable/equatable.dart';
import 'package:flutter/material.dart';

/// 健康服务类型枚举
enum HealthServiceType {
  /// 中医诊断
  tcmDiagnosis,
  
  /// 健康评估
  healthAssessment,
  
  /// 膳食指导
  dietGuidance,
  
  /// 运动处方
  exercisePrescription,
  
  /// 睡眠改善
  sleepImprovement,
  
  /// 心理调适
  mentalWellness,
  
  /// 慢病管理
  chronicDiseaseManagement,
  
  /// 亚健康调理
  subhealthConditioning,
}

/// 健康服务实体类
/// 定义应用中健康服务的核心属性和行为
class HealthService extends Equatable {
  /// 服务ID
  final String id;
  
  /// 服务名称
  final String name;
  
  /// 服务描述
  final String description;
  
  /// 服务类型
  final HealthServiceType type;
  
  /// 服务图标
  final IconData icon;
  
  /// 服务图片URL
  final String? imageUrl;
  
  /// 服务价格
  final double price;
  
  /// 服务是否需要付费
  final bool isPremium;
  
  /// 服务特色标签
  final List<String> tags;
  
  /// 服务详情路由
  final String routeName;
  
  /// 服务构造函数
  const HealthService({
    required this.id,
    required this.name,
    required this.description,
    required this.type,
    required this.icon,
    this.imageUrl,
    required this.price,
    this.isPremium = false,
    this.tags = const [],
    required this.routeName,
  });
  
  @override
  List<Object?> get props => [
    id,
    name,
    description,
    type,
    icon,
    imageUrl,
    price,
    isPremium,
    tags,
    routeName,
  ];
  
  /// 预设服务列表
  static List<HealthService> get presetServices => [
    // 中医诊断
    HealthService(
      id: 'tcm_diagnosis',
      name: '中医智能辩证',
      description: '基于传统中医理论，结合现代AI技术，通过问诊、望诊、舌诊等方式，为您提供体质分析和养生建议',
      type: HealthServiceType.tcmDiagnosis,
      icon: Icons.visibility,
      imageUrl: 'assets/images/services/tcm_diagnosis.jpg',
      price: 0,
      tags: ['AI辅助', '传统中医', '体质分析'],
      routeName: '/services/tcm-diagnosis',
    ),
    
    // 健康评估
    HealthService(
      id: 'health_assessment',
      name: '全面健康评估',
      description: '全面评估您的身体健康状况，包括基础健康指标、生活习惯分析、亚健康风险预警',
      type: HealthServiceType.healthAssessment,
      icon: Icons.assessment,
      imageUrl: 'assets/images/services/health_assessment.jpg',
      price: 0,
      tags: ['综合评估', '风险预警', '数据可视化'],
      routeName: '/services/health-assessment',
    ),
    
    // 膳食指导
    HealthService(
      id: 'diet_guidance',
      name: '个性化膳食指导',
      description: '根据您的体质特点和健康需求，提供个性化的膳食建议和食谱推荐',
      type: HealthServiceType.dietGuidance,
      icon: Icons.restaurant,
      imageUrl: 'assets/images/services/diet_guidance.jpg',
      price: 19.9,
      isPremium: true,
      tags: ['个性化推荐', '营养均衡', '中医食疗'],
      routeName: '/services/diet-guidance',
    ),
    
    // 运动处方
    HealthService(
      id: 'exercise_prescription',
      name: '科学运动处方',
      description: '基于您的身体状况和健康目标，设计科学的运动计划，帮助您有效提升身体素质',
      type: HealthServiceType.exercisePrescription,
      icon: Icons.directions_run,
      imageUrl: 'assets/images/services/exercise_prescription.jpg',
      price: 29.9,
      isPremium: true,
      tags: ['专业指导', '科学锻炼', '循序渐进'],
      routeName: '/services/exercise-prescription',
    ),
    
    // 睡眠改善
    HealthService(
      id: 'sleep_improvement',
      name: '睡眠质量改善',
      description: '通过科学方法分析您的睡眠问题，提供改善睡眠质量的专业建议',
      type: HealthServiceType.sleepImprovement,
      icon: Icons.bedtime,
      imageUrl: 'assets/images/services/sleep_improvement.jpg',
      price: 0,
      tags: ['睡眠监测', '舒缓放松', '作息调整'],
      routeName: '/services/sleep-improvement',
    ),
    
    // 心理调适
    HealthService(
      id: 'mental_wellness',
      name: '心理健康调适',
      description: '提供心理压力评估和调节方案，帮助您保持心理健康和情绪平衡',
      type: HealthServiceType.mentalWellness,
      icon: Icons.psychology,
      imageUrl: 'assets/images/services/mental_wellness.jpg',
      price: 39.9,
      isPremium: true,
      tags: ['压力管理', '情绪调节', '冥想练习'],
      routeName: '/services/mental-wellness',
    ),
    
    // 慢病管理
    HealthService(
      id: 'chronic_disease_management',
      name: '慢病健康管理',
      description: '针对高血压、糖尿病等慢性疾病，提供专业的健康管理方案',
      type: HealthServiceType.chronicDiseaseManagement,
      icon: Icons.monitor_heart,
      imageUrl: 'assets/images/services/chronic_disease_management.jpg',
      price: 49.9,
      isPremium: true,
      tags: ['长期跟踪', '指标监测', '综合干预'],
      routeName: '/services/chronic-disease',
    ),
    
    // 亚健康调理
    HealthService(
      id: 'subhealth_conditioning',
      name: '亚健康调理',
      description: '针对亚健康状态，提供综合调理方案，帮助您恢复健康状态',
      type: HealthServiceType.subhealthConditioning,
      icon: Icons.health_and_safety,
      imageUrl: 'assets/images/services/subhealth_conditioning.jpg',
      price: 0,
      tags: ['整体调理', '生活方式改善', '中西医结合'],
      routeName: '/services/subhealth',
    ),
  ];
} 