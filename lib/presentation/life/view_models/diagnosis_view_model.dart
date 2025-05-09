import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/domain/models/diagnosis_session_model.dart';
import 'package:suoke_life/domain/models/tongue_analysis_model.dart';
import 'package:suoke_life/domain/repositories/diagnosis_repository.dart';
import 'package:suoke_life/di/providers.dart';

/// 四诊视图模型状态
class DiagnosisState {
  /// 当前会话
  final DiagnosisSession? currentSession;
  
  /// 是否正在加载
  final bool isLoading;
  
  /// 错误信息
  final String? errorMessage;
  
  /// 当前步骤引导文本
  final String? currentGuidanceText;
  
  /// 当前舌象分析
  final TongueAnalysis? tongueAnalysis;
  
  /// 构造函数
  DiagnosisState({
    this.currentSession,
    this.isLoading = false,
    this.errorMessage,
    this.currentGuidanceText,
    this.tongueAnalysis,
  });
  
  /// 创建初始状态
  factory DiagnosisState.initial() {
    return DiagnosisState();
  }
  
  /// 复制状态并修改部分属性
  DiagnosisState copyWith({
    DiagnosisSession? currentSession,
    bool? isLoading,
    String? errorMessage,
    String? currentGuidanceText,
    TongueAnalysis? tongueAnalysis,
  }) {
    return DiagnosisState(
      currentSession: currentSession ?? this.currentSession,
      isLoading: isLoading ?? this.isLoading,
      errorMessage: errorMessage,
      currentGuidanceText: currentGuidanceText ?? this.currentGuidanceText,
      tongueAnalysis: tongueAnalysis ?? this.tongueAnalysis,
    );
  }
}

/// 四诊视图模型
class DiagnosisViewModel extends StateNotifier<DiagnosisState> {
  /// 四诊仓库
  final DiagnosisRepository _repository;
  
  /// 构造函数
  DiagnosisViewModel(this._repository) : super(DiagnosisState.initial());
  
  /// 开始新的四诊会话
  Future<void> startNewSession(String userId) async {
    try {
      state = state.copyWith(isLoading: true, errorMessage: null);
      
      // 创建新会话
      final session = await _repository.createSession(userId: userId);
      
      // 更新状态为进行中
      final updatedSession = await _repository.updateSessionStatus(
        session.id,
        DiagnosisSessionStatus.inProgress
      );
      
      // 更新状态
      state = state.copyWith(
        isLoading: false,
        currentSession: updatedSession,
        currentGuidanceText: _getGuidanceTextForStep(updatedSession.currentStep),
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: '创建四诊会话失败: $e',
      );
    }
  }
  
  /// 获取特定会话
  Future<void> getSession(String sessionId) async {
    try {
      state = state.copyWith(isLoading: true, errorMessage: null);
      
      // 获取会话
      final session = await _repository.getSessionById(sessionId);
      
      if (session == null) {
        state = state.copyWith(
          isLoading: false,
          errorMessage: '会话不存在',
        );
        return;
      }
      
      state = state.copyWith(
        isLoading: false,
        currentSession: session,
        currentGuidanceText: _getGuidanceTextForStep(session.currentStep),
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: '获取四诊会话失败: $e',
      );
    }
  }
  
  /// 更新当前步骤
  Future<void> updateCurrentStep(DiagnosisStep step) async {
    if (state.currentSession == null) {
      state = state.copyWith(
        errorMessage: '没有活跃的四诊会话',
      );
      return;
    }
    
    try {
      state = state.copyWith(isLoading: true, errorMessage: null);
      
      // 更新当前步骤
      final updatedSession = await _repository.updateSessionStep(
        state.currentSession!.id,
        step,
      );
      
      state = state.copyWith(
        isLoading: false,
        currentSession: updatedSession,
        currentGuidanceText: _getGuidanceTextForStep(step),
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: '更新四诊步骤失败: $e',
      );
    }
  }
  
  /// 完成当前步骤
  Future<void> completeCurrentStep(Map<String, dynamic> stepData, {DiagnosisStep? nextStep}) async {
    if (state.currentSession == null) {
      state = state.copyWith(
        errorMessage: '没有活跃的四诊会话',
      );
      return;
    }
    
    try {
      state = state.copyWith(isLoading: true, errorMessage: null);
      
      // 完成当前步骤
      final currentStep = state.currentSession!.currentStep;
      final updatedSession = await _repository.completeSessionStep(
        state.currentSession!.id,
        currentStep,
        stepData,
        nextStep: nextStep,
      );
      
      state = state.copyWith(
        isLoading: false,
        currentSession: updatedSession,
        currentGuidanceText: _getGuidanceTextForStep(updatedSession.currentStep),
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: '完成四诊步骤失败: $e',
      );
    }
  }
  
  /// 保存舌象分析
  Future<void> saveTongueAnalysis(TongueAnalysis analysis) async {
    try {
      state = state.copyWith(isLoading: true, errorMessage: null);
      
      // 保存舌象分析
      final savedAnalysis = await _repository.saveTongueAnalysis(analysis);
      
      // 如果有活跃会话，更新舌诊步骤数据
      if (state.currentSession != null) {
        await completeCurrentStep(
          {'tongue_analysis_id': savedAnalysis.id},
          nextStep: DiagnosisStep.symptomsInquiry,
        );
      }
      
      state = state.copyWith(
        isLoading: false,
        tongueAnalysis: savedAnalysis,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: '保存舌象分析失败: $e',
      );
    }
  }
  
  /// 完成四诊会话
  Future<void> completeSession() async {
    if (state.currentSession == null) {
      state = state.copyWith(
        errorMessage: '没有活跃的四诊会话',
      );
      return;
    }
    
    try {
      state = state.copyWith(isLoading: true, errorMessage: null);
      
      // 完成会话
      final updatedSession = await _repository.updateSessionStatus(
        state.currentSession!.id,
        DiagnosisSessionStatus.completed,
      );
      
      state = state.copyWith(
        isLoading: false,
        currentSession: updatedSession,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: '完成四诊会话失败: $e',
      );
    }
  }
  
  /// 获取不同步骤的引导文本
  String _getGuidanceTextForStep(DiagnosisStep step) {
    switch (step) {
      case DiagnosisStep.preparation:
        return '接下来我将引导您完成四诊采集，请准备好并放松心情。';
      case DiagnosisStep.tongueImage:
        return '请张口吐舌，拍摄清晰的舌象照片，光线要充足，尽量展示完整舌面。';
      case DiagnosisStep.faceObservation:
        return '请保持自然表情，面部放松，我将采集您的面色特征。';
      case DiagnosisStep.voiceRecording:
        return '请用平和的语气说一句"阳光明媚的早晨"，以便我分析您的声音特征。';
      case DiagnosisStep.symptomsInquiry:
        return '接下来我需要了解您的主要不适症状，请如实回答以下问题。';
      case DiagnosisStep.mentalInquiry:
        return '请简要描述您最近的情绪状态和睡眠质量。';
      case DiagnosisStep.lifestyleInquiry:
        return '请介绍一下您的日常饮食和运动习惯。';
      case DiagnosisStep.pulseGuidance:
        return '请找到手腕内侧的脉搏位置，按图示方法轻按，感受脉象特点。';
      case DiagnosisStep.analysis:
        return '正在综合分析您的四诊信息，请稍候...';
      case DiagnosisStep.recommendation:
        return '根据您的体质特点，我们为您生成了个性化的健康建议。';
    }
  }
}

/// 四诊视图模型提供者
final diagnosisViewModelProvider = StateNotifierProvider<DiagnosisViewModel, DiagnosisState>((ref) {
  final repository = ref.watch(diagnosisRepositoryProvider);
  return DiagnosisViewModel(repository);
}); 