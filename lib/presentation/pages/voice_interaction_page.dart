import 'package:flutter/material.dart';
import '../../services/voice_service.dart';
import '../../services/data_storage_service.dart';
import 'dart:async';

class VoiceInteractionPage extends StatefulWidget {
  const VoiceInteractionPage({super.key});

  @override
  State<VoiceInteractionPage> createState() => _VoiceInteractionPageState();
}

class _VoiceInteractionPageState extends State<VoiceInteractionPage> {
  final VoiceService _voiceService = VoiceService();
  final DataStorageService _storageService = DataStorageService();
  bool _isRecording = false;
  bool _isPlaying = false;
  String? _currentRecordingPath;
  List<Map<String, dynamic>> _recordings = [];
  Timer? _recordingTimer;
  int _recordingDuration = 0;

  @override
  void initState() {
    super.initState();
    _initializeServices();
    _loadRecordings();
  }

  Future<void> _initializeServices() async {
    try {
      await _voiceService.init();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('初始化失败: $e')),
        );
      }
    }
  }

  Future<void> _loadRecordings() async {
    try {
      final recordings = await _storageService.getVoiceRecords();
      setState(() {
        _recordings = recordings;
      });
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('加载录音失败: $e')),
        );
      }
    }
  }

  Future<void> _startRecording() async {
    try {
      await _voiceService.startRecording();
      setState(() {
        _isRecording = true;
        _recordingDuration = 0;
      });
      
      // 开始计时
      _recordingTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
        setState(() {
          _recordingDuration++;
        });
      });
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('开始录音失败: $e')),
      );
    }
  }

  Future<void> _stopRecording() async {
    try {
      _recordingTimer?.cancel();
      final path = await _voiceService.stopRecording();
      if (path != null) {
        _currentRecordingPath = path;
        // 保存录音记录
        await _storageService.saveVoiceRecord(
          content: '语音记录 ${DateTime.now()}',
          filePath: path,
          duration: _recordingDuration,
        );
        await _loadRecordings(); // 重新加载录音列表
      }
      setState(() {
        _isRecording = false;
        _recordingDuration = 0;
      });
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('停止录音失败: $e')),
      );
    }
  }

  Future<void> _playRecording(String path) async {
    try {
      if (_isPlaying) {
        await _voiceService.stopPlaying();
        setState(() {
          _isPlaying = false;
        });
      } else {
        await _voiceService.playRecording(path);
        setState(() {
          _isPlaying = true;
        });
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('播放失败: $e')),
      );
    }
  }

  String _formatDuration(int seconds) {
    final minutes = seconds ~/ 60;
    final remainingSeconds = seconds % 60;
    return '$minutes:${remainingSeconds.toString().padLeft(2, '0')}';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('语音交互'),
      ),
      body: Column(
        children: [
          // 录音控制区域
          Container(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                // 录音时长显示
                if (_isRecording)
                  Text(
                    '录音时长: ${_formatDuration(_recordingDuration)}',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                const SizedBox(height: 20),
                // 录音按钮
                ElevatedButton(
                  onPressed: _isRecording ? _stopRecording : _startRecording,
                  style: ElevatedButton.styleFrom(
                    shape: const CircleBorder(),
                    padding: const EdgeInsets.all(24),
                    backgroundColor: _isRecording ? Colors.red : Colors.blue,
                  ),
                  child: Icon(
                    _isRecording ? Icons.stop : Icons.mic,
                    size: 32,
                    color: Colors.white,
                  ),
                ),
              ],
            ),
          ),
          // 录音列表
          Expanded(
            child: ListView.builder(
              itemCount: _recordings.length,
              itemBuilder: (context, index) {
                final recording = _recordings[index];
                final isCurrentlyPlaying = _isPlaying && 
                    recording['file_path'] == _currentRecordingPath;
                
                return ListTile(
                  leading: Icon(
                    isCurrentlyPlaying ? Icons.pause_circle : Icons.play_circle,
                    color: isCurrentlyPlaying ? Colors.blue : null,
                  ),
                  title: Text(recording['content'] as String),
                  subtitle: Text(
                    '时长: ${_formatDuration(recording['duration'] as int)}',
                  ),
                  trailing: Text(
                    DateTime.parse(recording['timestamp'] as String)
                        .toLocal()
                        .toString()
                        .split('.')[0],
                  ),
                  onTap: () => _playRecording(recording['file_path'] as String),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _recordingTimer?.cancel();
    _voiceService.dispose();
    super.dispose();
  }
} 