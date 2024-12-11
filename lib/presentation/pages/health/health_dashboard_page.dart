import 'package:flutter/material.dart';
import '../../../services/ai/core_algorithm_service.dart';
import '../../../services/health/realtime_health_manager.dart';
import '../../../services/voice_service.dart';
import '../../widgets/health/health_analysis_dashboard.dart';
import '../../widgets/voice_wave_animation.dart';

class HealthDashboardPage extends StatefulWidget {
  final CoreAlgorithmService algorithmService;
  final RealtimeHealthManager healthManager;
  final VoiceService voiceService;

  const HealthDashboardPage({
    Key? key,
    required this.algorithmService,
    required this.healthManager,
    required this.voiceService,
  }) : super(key: key);

  @override
  State<HealthDashboardPage> createState() => _HealthDashboardPageState();
}

class _HealthDashboardPageState extends State<HealthDashboardPage> {
  bool _isRecording = false;
  bool _isProcessing = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('健康分析'),
        actions: [
          IconButton(
            icon: _isProcessing
                ? const SizedBox(
                    width: 24,
                    height: 24,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : Icon(_isRecording ? Icons.stop : Icons.mic),
            onPressed: _isProcessing ? null : _toggleRecording,
          ),
        ],
      ),
      body: Stack(
        children: [
          HealthAnalysisDashboard(
            algorithmService: widget.algorithmService,
            healthManager: widget.healthManager,
          ),
          if (_isRecording)
            Positioned(
              left: 0,
              right: 0,
              bottom: 0,
              child: Container(
                padding: const EdgeInsets.all(16),
                color: Theme.of(context).colorScheme.surface.withOpacity(0.9),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Text('正在录音...'),
                    const SizedBox(height: 8),
                    const VoiceWaveAnimation(),
                    const SizedBox(height: 8),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        TextButton(
                          onPressed: _cancelRecording,
                          child: const Text('取消'),
                        ),
                        const SizedBox(width: 16),
                        ElevatedButton(
                          onPressed: _stopRecording,
                          child: const Text('完成'),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }

  Future<void> _toggleRecording() async {
    if (_isRecording) {
      await _stopRecording();
    } else {
      await _startRecording();
    }
  }

  Future<void> _startRecording() async {
    try {
      await widget.voiceService.startRecording();
      setState(() {
        _isRecording = true;
      });
    } catch (e) {
      _showError('启动录音失败: $e');
    }
  }

  Future<void> _stopRecording() async {
    if (!_isRecording) return;

    setState(() {
      _isProcessing = true;
    });

    try {
      final voiceData = await widget.voiceService.stopRecording();
      await widget.healthManager.updateVoiceData(voiceData);
    } catch (e) {
      _showError('处理录音失败: $e');
    } finally {
      setState(() {
        _isRecording = false;
        _isProcessing = false;
      });
    }
  }

  Future<void> _cancelRecording() async {
    try {
      await widget.voiceService.cancelRecording();
    } catch (e) {
      _showError('取消录音失败: $e');
    } finally {
      setState(() {
        _isRecording = false;
      });
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red,
      ),
    );
  }
} 