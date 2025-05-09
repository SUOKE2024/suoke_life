import 'package:equatable/equatable.dart';
import 'package:flutter/foundation.dart';
import 'package:uuid/uuid.dart';

/// 四诊会话状态枚举
enum DiagnosisSessionStatus {
  /// 未开始
  notStarted,
  
  /// 进行中
  inProgress,
  
  /// 已暂停
  paused,
  
  /// 已完成
  completed,
  
  /// 已取消
  cancelled,
}

/// 四诊类型枚举
enum DiagnosisType {
  /// 望诊 - 观察
  looking,
  
  /// 闻诊 - 听声音和气味
  listening,
  
  /// 问诊 - 询问症状
  inquiry,
  
  /// 切诊 - 触摸检查
  palpation,
  
  /// 综合四诊
  comprehensive,
}

/// 四诊步骤枚举
enum DiagnosisStep {
  /// 准备阶段
  preparation,
  
  /// 舌诊采集
  tongueImage,
  
  /// 面诊采集
  faceObservation,
  
  /// 声音采集
  voiceRecording,
  
  /// 症状询问
  symptomsInquiry,
  
  /// 精神状态询问
  mentalInquiry,
  
  /// 生活习惯询问
  lifestyleInquiry,
  
  /// 脉诊引导
  pulseGuidance,
  
  /// 结果分析
  analysis,
  
  /// 建议生成
  recommendation,
}

/// 四诊会话模型
class DiagnosisSession extends Equatable {
  /// 会话ID
  final String id;
  
  /// 用户ID
  final String userId;
  
  /// 会话创建时间
  final DateTime createdAt;
  
  /// 最后更新时间
  final DateTime updatedAt;
  
  /// 会话状态
  final DiagnosisSessionStatus status;
  
  /// 当前诊断类型
  final DiagnosisType currentType;
  
  /// 当前诊断步骤
  final DiagnosisStep currentStep;
  
  /// 已完成的步骤
  final List<DiagnosisStep> completedSteps;
  
  /// 诊断数据（包含各步骤采集的结果）
  final Map<String, dynamic> diagnosisData;
  
  /// 会话附加数据
  final Map<String, dynamic>? extraData;

  /// 构造函数
  const DiagnosisSession({
    required this.id,
    required this.userId,
    required this.createdAt,
    required this.updatedAt,
    required this.status,
    required this.currentType,
    required this.currentStep,
    required this.completedSteps,
    required this.diagnosisData,
    this.extraData,
  });

  /// 创建新会话
  factory DiagnosisSession.create({
    required String userId,
    DiagnosisType initialType = DiagnosisType.comprehensive,
  }) {
    final now = DateTime.now();
    return DiagnosisSession(
      id: const Uuid().v4(),
      userId: userId,
      createdAt: now,
      updatedAt: now,
      status: DiagnosisSessionStatus.notStarted,
      currentType: initialType,
      currentStep: DiagnosisStep.preparation,
      completedSteps: [],
      diagnosisData: {},
    );
  }

  /// 判断会话是否完成
  bool get isCompleted => status == DiagnosisSessionStatus.completed;
  
  /// 判断会话是否活跃
  bool get isActive => status == DiagnosisSessionStatus.inProgress;
  
  /// 判断特定步骤是否已完成
  bool isStepCompleted(DiagnosisStep step) => completedSteps.contains(step);
  
  /// 获取会话进度百分比
  double get progressPercentage {
    final totalSteps = DiagnosisStep.values.length;
    final completed = completedSteps.length;
    return completed / totalSteps;
  }

  /// 复制会话并修改部分属性
  DiagnosisSession copyWith({
    String? id,
    String? userId,
    DateTime? createdAt,
    DateTime? updatedAt,
    DiagnosisSessionStatus? status,
    DiagnosisType? currentType,
    DiagnosisStep? currentStep,
    List<DiagnosisStep>? completedSteps,
    Map<String, dynamic>? diagnosisData,
    Map<String, dynamic>? extraData,
  }) {
    return DiagnosisSession(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      status: status ?? this.status,
      currentType: currentType ?? this.currentType,
      currentStep: currentStep ?? this.currentStep,
      completedSteps: completedSteps ?? this.completedSteps,
      diagnosisData: diagnosisData ?? this.diagnosisData,
      extraData: extraData ?? this.extraData,
    );
  }

  /// 标记步骤为已完成并更新数据
  DiagnosisSession completeStep(
    DiagnosisStep step, 
    Map<String, dynamic> stepData, 
    {DiagnosisStep? nextStep}
  ) {
    final newCompletedSteps = List<DiagnosisStep>.from(completedSteps);
    if (!newCompletedSteps.contains(step)) {
      newCompletedSteps.add(step);
    }
    
    final newDiagnosisData = Map<String, dynamic>.from(diagnosisData);
    newDiagnosisData.addAll(stepData);
    
    return copyWith(
      updatedAt: DateTime.now(),
      status: DiagnosisSessionStatus.inProgress,
      currentStep: nextStep ?? currentStep,
      completedSteps: newCompletedSteps,
      diagnosisData: newDiagnosisData,
    );
  }

  /// 开始会话
  DiagnosisSession start() {
    return copyWith(
      updatedAt: DateTime.now(),
      status: DiagnosisSessionStatus.inProgress,
    );
  }

  /// 暂停会话
  DiagnosisSession pause() {
    return copyWith(
      updatedAt: DateTime.now(),
      status: DiagnosisSessionStatus.paused,
    );
  }

  /// 完成会话
  DiagnosisSession complete() {
    return copyWith(
      updatedAt: DateTime.now(),
      status: DiagnosisSessionStatus.completed,
    );
  }

  /// 取消会话
  DiagnosisSession cancel() {
    return copyWith(
      updatedAt: DateTime.now(),
      status: DiagnosisSessionStatus.cancelled,
    );
  }

  /// 从JSON创建会话模型
  factory DiagnosisSession.fromJson(Map<String, dynamic> json) {
    return DiagnosisSession(
      id: json['id'],
      userId: json['user_id'],
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
      status: DiagnosisSessionStatus.values.byName(json['status']),
      currentType: DiagnosisType.values.byName(json['current_type']),
      currentStep: DiagnosisStep.values.byName(json['current_step']),
      completedSteps: (json['completed_steps'] as List)
          .map((step) => DiagnosisStep.values.byName(step))
          .toList(),
      diagnosisData: json['diagnosis_data'],
      extraData: json['extra_data'],
    );
  }

  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
      'status': status.name,
      'current_type': currentType.name,
      'current_step': currentStep.name,
      'completed_steps': completedSteps.map((step) => step.name).toList(),
      'diagnosis_data': diagnosisData,
      'extra_data': extraData,
    };
  }

  @override
  List<Object?> get props => [
    id,
    userId,
    status,
    currentType,
    currentStep,
    completedSteps,
    diagnosisData,
    extraData,
  ];
} 