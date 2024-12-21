import 'package:flutter/material.dart';
import 'dart:async';
import 'package:record/record.dart';
import 'package:permission_handler/permission_handler.dart';

class VoiceRecorder extends StatefulWidget {
  final Function(String, int) onRecordComplete;
  final Function() onRecordCancel;

  const VoiceRecorder({
    Key? key,
    required this.onRecordComplete,
    required this.onRecordCancel,
  }) : super(key: key);

  @override
  State<VoiceRecorder> createState() => _VoiceRecorderState();
}

class _VoiceRecorderState extends State<VoiceRecorder> {
  final _record = Record();
  Timer? _timer;
  int _duration = 0;
  bool _isRecording = false;
  String? _recordPath;

  @override
  void dispose() {
    _timer?.cancel();
    _record.dispose();
    super.dispose();
  }

  Future<void> _startRecording() async {
    try {
      if (await Permission.microphone.request().isGranted) {
        await _record.start();
        _recordPath = await _record.getPath();
        setState(() {
          _isRecording = true;
          _duration = 0;
        });
        _startTimer();
      }
    } catch (e) {
      debugPrint('录音失败: $e');
    }
  }

  Future<void> _stopRecording() async {
    _timer?.cancel();
    if (_isRecording) {
      final path = await _record.stop();
      setState(() => _isRecording = false);
      if (path != null) {
        widget.onRecordComplete(path, _duration);
      }
    }
  }

  void _cancelRecording() async {
    _timer?.cancel();
    if (_isRecording) {
      await _record.stop();
      setState(() => _isRecording = false);
      widget.onRecordCancel();
    }
  }

  void _startTimer() {
    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      setState(() => _duration++);
      if (_duration >= 60) {
        _stopRecording();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onLongPressStart: (_) => _startRecording(),
      onLongPressEnd: (_) => _stopRecording(),
      onLongPressCancel: _cancelRecording,
      child: Container(
        height: 50,
        width: double.infinity,
        decoration: BoxDecoration(
          color: _isRecording ? Colors.red.withOpacity(0.1) : Colors.grey[200],
          borderRadius: BorderRadius.circular(25),
        ),
        child: Center(
          child: Text(
            _isRecording ? '松开发送 ${_duration}s' : '按住说话',
            style: TextStyle(
              color: _isRecording ? Colors.red : Colors.grey[600],
            ),
          ),
        ),
      ),
    );
  }
} 