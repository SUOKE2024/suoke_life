import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:uuid/uuid.dart';
import 'package:suoke_life/data/services/sleep_analysis_service_impl.dart';
import 'package:suoke_life/di/providers.dart';
import 'package:suoke_life/domain/models/health_record_model.dart';
import 'package:suoke_life/domain/models/sleep_analysis_model.dart';
import 'package:suoke_life/domain/repositories/health_repository.dart';
import 'package:suoke_life/domain/services/sleep_analysis_service.dart';

/// 睡眠分析状态
class SleepAnalysisState {
  /// 是否加载中
  final bool isLoading;
  
  /// 错误信息
  final String? errorMessage;
  
  /// 睡眠分析列表
  final List<SleepAnalysis> analyses;
  
  /// 当前查看的分析
  final SleepAnalysis? currentAnalysis;
  
  /// 分析结果
  final SleepAnalysisResult? result;
  
  /// 改善建议
  final List<String> suggestions;
  
  /// 趋势数据
  final Map<String, dynamic>? trendData;

  /// 构造函数
  const SleepAnalysisState({
    this.isLoading = false,
    this.errorMessage,
    this.analyses = const [],
    this.currentAnalysis,
    this.result,
    this.suggestions = const [],
    this.trendData,
  });

  /// 复制方法
  SleepAnalysisState copyWith({
    bool? isLoading,
    String? errorMessage,
    List<SleepAnalysis>? analyses,
    SleepAnalysis? currentAnalysis,
    SleepAnalysisResult? result,
    List<String>? suggestions,
    Map<String, dynamic>? trendData,
  }) {
    return SleepAnalysisState(
      isLoading: isLoading ?? this.isLoading,
      errorMessage: errorMessage,
      analyses: analyses ?? this.analyses,
      currentAnalysis: currentAnalysis ?? this.currentAnalysis,
      result: result ?? this.result,
      suggestions: suggestions ?? this.suggestions,
      trendData: trendData ?? this.trendData,
    );
  }
}

/// 睡眠分析视图模型
class SleepAnalysisViewModel extends StateNotifier<SleepAnalysisState> {
  /// 睡眠分析服务
  final SleepAnalysisService _sleepAnalysisService;
  
  /// 健康仓库
  final HealthRepository _healthRepository;

  /// 构造函数
  SleepAnalysisViewModel(this._sleepAnalysisService, this._healthRepository)
      : super(const SleepAnalysisState());

  /// 获取最近睡眠分析
  Future<void> getRecentAnalyses(int count) async {
    state = state.copyWith(isLoading: true, errorMessage: null);

    try {
      final analyses = await _sleepAnalysisService.getRecentAnalyses(
        'current_user',
        count,
      );
      state = state.copyWith(isLoading: false, analyses: analyses);
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: '获取睡眠分析失败: ${e.toString()}',
      );
    }
  }

  /// 获取睡眠分析详情
  Future<void> getAnalysis(String recordId) async {
    state = state.copyWith(isLoading: true, errorMessage: null);

    try {
      final analysisResult = await _sleepAnalysisService.generateAnalysis(recordId);
      
      // 获取记录以创建SleepAnalysis对象
      final record = await _healthRepository.getRecordById(recordId);
      if (record != null && record.type == HealthDataType.sleep) {
        // 创建睡眠分析对象
        final sleepAnalysis = SleepAnalysis.fromResult(
          recordId,
          analysisResult,
        );
        
        state = state.copyWith(
          isLoading: false,
          currentAnalysis: sleepAnalysis,
          result: analysisResult,
        );
      } else {
        state = state.copyWith(
          isLoading: false,
          result: analysisResult,
          errorMessage: '无法获取睡眠记录',
        );
      }
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: '获取睡眠分析详情失败: ${e.toString()}',
      );
    }
  }
  
  /// 分析睡眠记录
  Future<void> analyzeSleepRecord(String recordId) async {
    state = state.copyWith(isLoading: true, errorMessage: null);

    try {
      // 获取记录
      final record = await _healthRepository.getRecordById(recordId);
      
      if (record == null || record.type != HealthDataType.sleep) {
        throw Exception('无效的睡眠记录');
      }
      
      // 分析睡眠记录
      final analysis = await _sleepAnalysisService.analyzeSleepRecord(record as SleepRecord);
      
      // 获取改善建议
      final suggestions = await _sleepAnalysisService.generateSleepImprovementSuggestions(
        record as SleepRecord,
        analysis,
      );
      
      // 获取中医评估
      final tcmEvaluation = await _sleepAnalysisService.getTCMEvaluation(
        record as SleepRecord,
        analysis,
      );
      
      // 创建睡眠分析对象
      final sleepAnalysis = SleepAnalysis.fromResult(
        recordId,  // 使用记录ID作为分析ID
        analysis,
      );
      
      state = state.copyWith(
        isLoading: false,
        currentAnalysis: sleepAnalysis,
        result: analysis,
        suggestions: suggestions,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: '分析睡眠记录失败: ${e.toString()}',
      );
    }
  }
  
  /// 分析睡眠趋势
  Future<void> analyzeSleepTrend(DateTime startDate, DateTime endDate) async {
    state = state.copyWith(isLoading: true, errorMessage: null);

    try {
      // 获取分析结果
      final result = await _sleepAnalysisService.analyzeSleepTrend(
        'current_user', // 当前用户ID
        startDate,
        endDate,
      );
      
      // 更新状态
      state = state.copyWith(
        isLoading: false,
        trendData: result,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: '分析睡眠趋势失败: ${e.toString()}',
      );
    }
  }
}
