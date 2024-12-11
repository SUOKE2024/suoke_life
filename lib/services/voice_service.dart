import 'dart:async';
import 'package:flutter_sound/flutter_sound.dart';
import 'package:permission_handler/permission_handler.dart';

import 'dart:io';

class VoiceService {
  FlutterSoundRecorder? _recorder;
  FlutterSoundPlayer? _player;
  bool _isRecorderInitialized = false;
  bool _isPlayerInitialized = false;
  String? _recordingPath;

  Future<void> init() async {
    _recorder = FlutterSoundRecorder();
    _player = FlutterSoundPlayer();
    
    // 请求麦克风权限
    final status = await Permission.microphone.request();
    if (status != PermissionStatus.granted) {
      throw Exception('需要麦克风权限来录音');
    }

    await _recorder!.openRecorder();
    await _player!.openPlayer();
    
    _isRecorderInitialized = true;
    _isPlayerInitialized = true;
  }

  Future<void> startRecording() async {
    if (!_isRecorderInitialized) {
      throw Exception('录音器未初始化');
    }

    // 创建临时文件路径
    final dir = await getTemporaryDirectory();
    _recordingPath = '${dir.path}/recording_${DateTime.now().millisecondsSinceEpoch}.aac';

    await _recorder!.startRecorder(
      toFile: _recordingPath,
      codec: Codec.aacADTS,
    );
  }

  Future<String?> stopRecording() async {
    if (!_isRecorderInitialized) {
      throw Exception('录音器未初始化');
    }

    await _recorder!.stopRecorder();
    return _recordingPath;
  }

  Future<void> playRecording(String path) async {
    if (!_isPlayerInitialized) {
      throw Exception('播放器未初始化');
    }

    await _player!.startPlayer(
      fromURI: path,
      codec: Codec.aacADTS,
    );
  }

  Future<void> stopPlaying() async {
    if (!_isPlayerInitialized) {
      throw Exception('播放器未初始化');
    }

    await _player!.stopPlayer();
  }

  Future<void> dispose() async {
    if (_isRecorderInitialized) {
      await _recorder!.closeRecorder();
      _recorder = null;
      _isRecorderInitialized = false;
    }

    if (_isPlayerInitialized) {
      await _player!.closePlayer();
      _player = null;
      _isPlayerInitialized = false;
    }

    // 清理临时录音文件
    if (_recordingPath != null) {
      final file = File(_recordingPath!);
      if (await file.exists()) {
        await file.delete();
      }
    }
  }
} 