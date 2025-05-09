import 'dart:async';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:path_provider/path_provider.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'package:suoke_life/presentation/life/view_models/diagnosis_view_model.dart';
import 'package:suoke_life/domain/models/diagnosis_session_model.dart';
import 'package:suoke_life/presentation/widgets/loading_overlay.dart';

/// 声音记录页面
class VoiceRecordingScreen extends ConsumerStatefulWidget {
  /// 会话ID
  final String? sessionId;

  /// 构造函数
  const VoiceRecordingScreen({
    super.key,
    this.sessionId,
  });

  @override
  ConsumerState<VoiceRecordingScreen> createState() => _VoiceRecordingScreenState();
}

class _VoiceRecordingScreenState extends ConsumerState<VoiceRecordingScreen> {
  // 语音识别实例
  final stt.SpeechToText _speech = stt.SpeechToText();
  bool _isListening = false;
  String _recognizedText = '';
  String _voiceFilePath = '';
  bool _isInitialized = false;
  
  // 语音分析相关
  double _pitch = 0.0;
  double _volume = 0.0;
  double _speed = 0.0;
  String _voiceAnalysisResult = '';
  bool _isAnalyzing = false;
  
  // 计时器
  int _recordDuration = 0;
  Timer? _timer;
  
  @override
  void initState() {
    super.initState();
    _initSpeech();
    
    // 如果有会话ID，获取会话信息
    if (widget.sessionId != null) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        ref.read(diagnosisViewModelProvider.notifier).getSession(widget.sessionId!);
      });
    }
  }
  
  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }
  
  /// 初始化语音识别
  Future<void> _initSpeech() async {
    bool available = await _speech.initialize(
      onStatus: _onSpeechStatus,
      onError: _onSpeechError,
    );
    
    if (available) {
      setState(() {
        _isInitialized = true;
      });
    } else {
      _showError('语音识别功能不可用');
    }
  }
  
  /// 语音状态回调
  void _onSpeechStatus(String status) {
    if (status == 'notListening') {
      setState(() {
        _isListening = false;
      });
      _timer?.cancel();
    }
  }
  
  /// 语音错误回调
  void _onSpeechError(dynamic error) {
    _showError('语音识别错误: $error');
    setState(() {
      _isListening = false;
    });
    _timer?.cancel();
  }
  
  /// 开始录音
  void _startListening() async {
    if (_isAnalyzing) return;
    
    if (!_isInitialized) {
      await _initSpeech();
    }
    
    if (_isInitialized) {
      // 重置状态
      setState(() {
        _recognizedText = '';
        _recordDuration = 0;
        _isListening = true;
      });
      
      // 启动定时器
      _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
        setState(() {
          _recordDuration++;
        });
      });
      
      // 开始录音
      await _speech.listen(
        onResult: (result) {
          setState(() {
            _recognizedText = result.recognizedWords;
          });
        },
        localeId: 'zh_CN',
      );
      
      // 生成临时文件路径
      final directory = await getApplicationDocumentsDirectory();
      final timestamp = DateTime.now().millisecondsSinceEpoch;
      _voiceFilePath = '${directory.path}/voice_records/voice_$timestamp.wav';
      
      // 确保目录存在
      final voiceDir = Directory(File(_voiceFilePath).parent.path);
      if (!await voiceDir.exists()) {
        await voiceDir.create(recursive: true);
      }
      
      // 注意：这里只是模拟文件保存，实际应用中需要使用专门的录音插件
      // 例如flutter_sound或record来实际保存录音文件
    } else {
      _showError('无法初始化语音识别');
    }
  }
  
  /// 停止录音
  void _stopListening() {
    if (_isListening) {
      _speech.stop();
      _timer?.cancel();
      
      setState(() {
        _isListening = false;
      });
      
      // 分析声音特征
      _analyzeVoice();
    }
  }
  
  /// 分析声音特征（模拟）
  Future<void> _analyzeVoice() async {
    if (_recognizedText.isEmpty) {
      _showError('未识别到语音内容，请重试');
      return;
    }
    
    setState(() {
      _isAnalyzing = true;
    });
    
    try {
      // 模拟分析过程
      await Future.delayed(const Duration(seconds: 2));
      
      // 模拟分析结果（实际应用中应该基于真实的声音分析）
      setState(() {
        // 随机模拟一些特征值
        _pitch = 0.6 + (DateTime.now().millisecond % 40) / 100; // 0.6-1.0
        _volume = 0.5 + (DateTime.now().millisecond % 50) / 100; // 0.5-1.0
        _speed = 0.7 + (DateTime.now().millisecond % 30) / 100; // 0.7-1.0
        
        // 生成分析结果（实际应用中应基于真实分析）
        _generateVoiceAnalysisResult();
        
        _isAnalyzing = false;
      });
      
      // 如果在四诊会话中，更新会话状态
      final state = ref.read(diagnosisViewModelProvider);
      if (state.currentSession != null) {
        await ref.read(diagnosisViewModelProvider.notifier).completeCurrentStep(
          {
            'voice_record_path': _voiceFilePath,
            'voice_text': _recognizedText,
            'voice_features': {
              'pitch': _pitch,
              'volume': _volume,
              'speed': _speed,
            },
            'voice_analysis': _voiceAnalysisResult,
          },
          nextStep: DiagnosisStep.symptomsInquiry,
        );
      }
    } catch (e) {
      _showError('声音分析失败: $e');
      setState(() {
        _isAnalyzing = false;
      });
    }
  }
  
  /// 生成声音分析结果
  void _generateVoiceAnalysisResult() {
    String result = '';
    
    // 声调分析
    if (_pitch > 0.8) {
      result += '声音偏高，可能提示体内有热；';
    } else if (_pitch < 0.7) {
      result += '声音偏低沉，可能提示体内有寒；';
    } else {
      result += '声调适中，体内寒热较为平衡；';
    }
    
    // 音量分析
    if (_volume > 0.8) {
      result += '声音洪亮，气息充足，提示气血较为充盈；';
    } else if (_volume < 0.6) {
      result += '声音较弱，可能提示气虚；';
    } else {
      result += '音量适中，气息均匀；';
    }
    
    // 语速分析
    if (_speed > 0.9) {
      result += '语速较快，可能提示心火旺盛；';
    } else if (_speed < 0.75) {
      result += '语速偏慢，可能提示脾胃功能减弱；';
    } else {
      result += '语速平和，精神状态较为稳定；';
    }
    
    _voiceAnalysisResult = result;
  }
  
  /// 显示错误信息
  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red,
      ),
    );
  }
  
  /// 格式化录音时长
  String _formatDuration() {
    final minutes = (_recordDuration ~/ 60).toString().padLeft(2, '0');
    final seconds = (_recordDuration % 60).toString().padLeft(2, '0');
    return '$minutes:$seconds';
  }
  
  @override
  Widget build(BuildContext context) {
    final state = ref.watch(diagnosisViewModelProvider);
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('声音采集'),
        elevation: 0,
      ),
      body: Stack(
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.center,
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
                    child: Text(
                      state.currentGuidanceText!,
                      style: const TextStyle(fontSize: 16),
                    ),
                  ),
                
                // 示例文本
                if (!_voiceAnalysisResult.isNotEmpty)
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.grey.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Column(
                      children: [
                        const Text(
                          '请用平和的语气朗读以下句子：',
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 16,
                          ),
                        ),
                        const SizedBox(height: 12),
                        Text(
                          '"阳光明媚的早晨，我在花园里散步，感受着春天的气息。"',
                          style: TextStyle(
                            fontSize: 18,
                            color: Theme.of(context).colorScheme.primary,
                          ),
                        ),
                      ],
                    ),
                  ),
                
                const SizedBox(height: 32),
                
                // 语音波形动画（简化版）
                Container(
                  height: 120,
                  decoration: BoxDecoration(
                    color: Colors.grey.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: _isListening
                      ? Center(
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: List.generate(7, (index) {
                              return Container(
                                margin: const EdgeInsets.symmetric(horizontal: 4),
                                width: 8,
                                height: 30 + (index * 10) + (DateTime.now().millisecond % 40),
                                decoration: BoxDecoration(
                                  color: Theme.of(context).colorScheme.primary,
                                  borderRadius: BorderRadius.circular(5),
                                ),
                              );
                            }),
                          ),
                        )
                      : const Center(
                          child: Text('点击下方按钮开始录音'),
                        ),
                ),
                
                // 时长显示
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  child: Text(
                    _formatDuration(),
                    style: const TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                
                // 识别结果
                if (_recognizedText.isNotEmpty)
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(16),
                    margin: const EdgeInsets.only(bottom: 16),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(12),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.grey.withOpacity(0.2),
                          spreadRadius: 1,
                          blurRadius: 4,
                          offset: const Offset(0, 2),
                        ),
                      ],
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          '识别结果:',
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 16,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(_recognizedText),
                      ],
                    ),
                  ),
                
                // 分析结果
                if (_voiceAnalysisResult.isNotEmpty)
                  Expanded(
                    child: Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(16),
                      margin: const EdgeInsets.only(bottom: 16),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(12),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.grey.withOpacity(0.2),
                            spreadRadius: 1,
                            blurRadius: 4,
                            offset: const Offset(0, 2),
                          ),
                        ],
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            '声音分析结果:',
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 16,
                            ),
                          ),
                          const SizedBox(height: 16),
                          
                          // 特征值显示
                          Row(
                            children: [
                              _buildFeatureIndicator('声调', _pitch),
                              const SizedBox(width: 16),
                              _buildFeatureIndicator('音量', _volume),
                              const SizedBox(width: 16),
                              _buildFeatureIndicator('语速', _speed),
                            ],
                          ),
                          
                          const SizedBox(height: 24),
                          
                          // 分析文本
                          Text(
                            _voiceAnalysisResult,
                            style: const TextStyle(
                              fontSize: 15,
                              height: 1.5,
                            ),
                          ),
                          
                          const Spacer(),
                          
                          // 继续按钮
                          SizedBox(
                            width: double.infinity,
                            child: ElevatedButton(
                              onPressed: () {
                                Navigator.of(context).pop();
                              },
                              style: ElevatedButton.styleFrom(
                                padding: const EdgeInsets.symmetric(vertical: 16),
                              ),
                              child: const Text('继续'),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                
                const Spacer(),
                
                // 录音按钮
                if (!_isAnalyzing && _voiceAnalysisResult.isEmpty)
                  GestureDetector(
                    onTapDown: (_) => _startListening(),
                    onTapUp: (_) => _stopListening(),
                    onTapCancel: () => _stopListening(),
                    child: Container(
                      width: 80,
                      height: 80,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: _isListening
                            ? Colors.red
                            : Theme.of(context).colorScheme.primary,
                        boxShadow: [
                          BoxShadow(
                            color: (_isListening ? Colors.red : Theme.of(context).colorScheme.primary).withOpacity(0.3),
                            spreadRadius: 5,
                            blurRadius: 10,
                            offset: const Offset(0, 3),
                          ),
                        ],
                      ),
                      child: Icon(
                        _isListening ? Icons.mic : Icons.mic_none,
                        color: Colors.white,
                        size: 40,
                      ),
                    ),
                  ),
                
                const SizedBox(height: 32),
                
                // 提示文本
                if (!_isAnalyzing && _voiceAnalysisResult.isEmpty)
                  Text(
                    _isListening ? '请说话...' : '按住按钮开始录音',
                    style: TextStyle(
                      color: Colors.grey[700],
                      fontSize: 16,
                    ),
                  ),
              ],
            ),
          ),
          
          // 加载遮罩
          if (_isAnalyzing || state.isLoading)
            const LoadingOverlay(message: '正在分析声音特征...'),
        ],
      ),
    );
  }
  
  /// 构建特征指示器
  Widget _buildFeatureIndicator(String label, double value) {
    return Expanded(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: const TextStyle(
              fontSize: 14,
              color: Colors.grey,
            ),
          ),
          const SizedBox(height: 8),
          LinearProgressIndicator(
            value: value,
            minHeight: 8,
            borderRadius: BorderRadius.circular(4),
          ),
          const SizedBox(height: 4),
          Text(
            '${(value * 100).toInt()}%',
            style: const TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }
} 