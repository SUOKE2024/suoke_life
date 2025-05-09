import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/domain/models/diagnosis_session_model.dart';
import 'package:suoke_life/presentation/life/view_models/diagnosis_view_model.dart';
import 'package:suoke_life/presentation/life/tongue_image_capture_screen.dart';
import 'package:suoke_life/presentation/life/symptoms_inquiry_screen.dart';
import 'package:suoke_life/presentation/life/voice_recording_screen.dart';
import 'package:suoke_life/presentation/life/pulse_guidance_screen.dart';
import 'package:suoke_life/presentation/life/diagnosis_result_screen.dart';
import 'package:suoke_life/presentation/widgets/loading_overlay.dart';

/// 四诊流程导航页面
class DiagnosisNavigatorScreen extends ConsumerStatefulWidget {
  /// 用户ID
  final String userId;
  
  /// 会话ID，如果为null则创建新会话
  final String? sessionId;

  /// 构造函数
  const DiagnosisNavigatorScreen({
    super.key,
    required this.userId,
    this.sessionId,
  });

  @override
  ConsumerState<DiagnosisNavigatorScreen> createState() => _DiagnosisNavigatorScreenState();
}

class _DiagnosisNavigatorScreenState extends ConsumerState<DiagnosisNavigatorScreen> {
  @override
  void initState() {
    super.initState();
    
    // 加载会话或创建新会话
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _initSession();
    });
  }
  
  /// 初始化会话
  Future<void> _initSession() async {
    final viewModel = ref.read(diagnosisViewModelProvider.notifier);
    
    if (widget.sessionId != null) {
      // 加载现有会话
      await viewModel.getSession(widget.sessionId!);
    } else {
      // 创建新会话
      await viewModel.startNewSession(widget.userId);
    }
  }
  
  /// 导航到对应步骤页面
  void _navigateToStep(DiagnosisStep step, BuildContext context) {
    final state = ref.read(diagnosisViewModelProvider);
    if (state.currentSession == null) return;
    
    // 根据步骤类型导航到相应页面
    switch (step) {
      case DiagnosisStep.tongueImage:
        Navigator.of(context).push(
          MaterialPageRoute(
            builder: (context) => const TongueImageCaptureScreen(),
          ),
        );
        break;
      case DiagnosisStep.voiceRecording:
        Navigator.of(context).push(
          MaterialPageRoute(
            builder: (context) => VoiceRecordingScreen(
              sessionId: state.currentSession!.id,
            ),
          ),
        );
        break;
      case DiagnosisStep.symptomsInquiry:
      case DiagnosisStep.mentalInquiry:
      case DiagnosisStep.lifestyleInquiry:
        Navigator.of(context).push(
          MaterialPageRoute(
            builder: (context) => SymptomsInquiryScreen(
              sessionId: state.currentSession!.id,
            ),
          ),
        );
        break;
      case DiagnosisStep.pulseGuidance:
        Navigator.of(context).push(
          MaterialPageRoute(
            builder: (context) => PulseGuidanceScreen(
              sessionId: state.currentSession!.id,
            ),
          ),
        );
        break;
      case DiagnosisStep.analysis:
      case DiagnosisStep.recommendation:
        Navigator.of(context).push(
          MaterialPageRoute(
            builder: (context) => DiagnosisResultScreen(
              sessionId: state.currentSession!.id,
            ),
          ),
        );
        break;
      // TODO: 实现其他步骤导航
      default:
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('暂未实现${_getStepName(step)}功能')),
        );
        break;
    }
  }
  
  /// 获取步骤名称
  String _getStepName(DiagnosisStep step) {
    switch (step) {
      case DiagnosisStep.preparation:
        return '准备';
      case DiagnosisStep.tongueImage:
        return '舌诊';
      case DiagnosisStep.faceObservation:
        return '面诊';
      case DiagnosisStep.voiceRecording:
        return '声音采集';
      case DiagnosisStep.symptomsInquiry:
        return '症状问诊';
      case DiagnosisStep.mentalInquiry:
        return '精神状态询问';
      case DiagnosisStep.lifestyleInquiry:
        return '生活习惯询问';
      case DiagnosisStep.pulseGuidance:
        return '脉诊引导';
      case DiagnosisStep.analysis:
        return '结果分析';
      case DiagnosisStep.recommendation:
        return '健康建议';
    }
  }
  
  /// 获取步骤图标
  IconData _getStepIcon(DiagnosisStep step) {
    switch (step) {
      case DiagnosisStep.preparation:
        return Icons.flight_takeoff;
      case DiagnosisStep.tongueImage:
        return Icons.camera_alt;
      case DiagnosisStep.faceObservation:
        return Icons.face;
      case DiagnosisStep.voiceRecording:
        return Icons.mic;
      case DiagnosisStep.symptomsInquiry:
        return Icons.question_answer;
      case DiagnosisStep.mentalInquiry:
        return Icons.psychology;
      case DiagnosisStep.lifestyleInquiry:
        return Icons.restaurant;
      case DiagnosisStep.pulseGuidance:
        return Icons.favorite;
      case DiagnosisStep.analysis:
        return Icons.analytics;
      case DiagnosisStep.recommendation:
        return Icons.health_and_safety;
    }
  }
  
  @override
  Widget build(BuildContext context) {
    final state = ref.watch(diagnosisViewModelProvider);
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('四诊流程'),
        elevation: 0,
      ),
      body: Stack(
        children: [
          // 内容区域
          state.currentSession == null
              ? const Center(child: CircularProgressIndicator())
              : SingleChildScrollView(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // 引导文本
                      if (state.currentGuidanceText != null)
                        Container(
                          width: double.infinity,
                          padding: const EdgeInsets.all(16),
                          margin: const EdgeInsets.only(bottom: 24),
                          decoration: BoxDecoration(
                            color: Theme.of(context).colorScheme.primary.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(
                              color: Theme.of(context).colorScheme.primary.withOpacity(0.3),
                            ),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                children: [
                                  Icon(
                                    Icons.lightbulb_outline,
                                    color: Theme.of(context).colorScheme.primary,
                                  ),
                                  const SizedBox(width: 8),
                                  const Text(
                                    '四诊引导',
                                    style: TextStyle(
                                      fontWeight: FontWeight.bold,
                                      fontSize: 16,
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 8),
                              Text(
                                state.currentGuidanceText!,
                                style: const TextStyle(fontSize: 15),
                              ),
                            ],
                          ),
                        ),
                      
                      // 步骤列表
                      ...DiagnosisStep.values.map((step) {
                        final isCompleted = state.currentSession!.isStepCompleted(step);
                        final isCurrent = state.currentSession!.currentStep == step;
                        
                        return Card(
                          margin: const EdgeInsets.only(bottom: 12),
                          elevation: isCurrent ? 3 : 1,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                            side: isCurrent
                                ? BorderSide(
                                    color: Theme.of(context).colorScheme.primary,
                                    width: 2,
                                  )
                                : BorderSide.none,
                          ),
                          child: ListTile(
                            contentPadding: const EdgeInsets.symmetric(
                              vertical: 8,
                              horizontal: 16,
                            ),
                            leading: CircleAvatar(
                              backgroundColor: isCompleted
                                  ? Colors.green
                                  : isCurrent
                                      ? Theme.of(context).colorScheme.primary
                                      : Colors.grey,
                              child: isCompleted
                                  ? const Icon(Icons.check, color: Colors.white)
                                  : Icon(_getStepIcon(step), color: Colors.white),
                            ),
                            title: Text(
                              _getStepName(step),
                              style: TextStyle(
                                fontWeight: isCurrent ? FontWeight.bold : FontWeight.normal,
                              ),
                            ),
                            subtitle: Text(isCompleted
                                ? '已完成'
                                : isCurrent
                                    ? '当前步骤'
                                    : '未开始'),
                            trailing: isCurrent
                                ? ElevatedButton(
                                    onPressed: () => _navigateToStep(step, context),
                                    child: const Text('开始'),
                                  )
                                : !isCompleted
                                    ? const Icon(Icons.lock, color: Colors.grey)
                                    : IconButton(
                                        icon: const Icon(Icons.visibility),
                                        onPressed: () => _navigateToStep(step, context),
                                      ),
                          ),
                        );
                      }).toList(),
                      
                      const SizedBox(height: 24),
                      
                      // 进度指示器
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              const Text(
                                '总体进度',
                                style: TextStyle(
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              Text(
                                '${(state.currentSession!.progressPercentage * 100).toInt()}%',
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 8),
                          LinearProgressIndicator(
                            value: state.currentSession!.progressPercentage,
                            minHeight: 10,
                            borderRadius: BorderRadius.circular(8),
                          ),
                        ],
                      ),
                      
                      // 如果完成了至少一半步骤，显示直接查看结果的按钮
                      if (state.currentSession!.progressPercentage >= 0.5) ...[
                        const SizedBox(height: 24),
                        SizedBox(
                          width: double.infinity,
                          child: ElevatedButton.icon(
                            icon: const Icon(Icons.analytics),
                            label: const Text('查看当前分析结果'),
                            style: ElevatedButton.styleFrom(
                              padding: const EdgeInsets.symmetric(vertical: 16),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(12),
                              ),
                            ),
                            onPressed: () => _navigateToStep(DiagnosisStep.analysis, context),
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
          
          // 加载遮罩
          if (state.isLoading) const LoadingOverlay(message: '加载中...'),
        ],
      ),
    );
  }
} 