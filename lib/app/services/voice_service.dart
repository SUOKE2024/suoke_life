import 'package:get/get.dart';
import 'package:record/record.dart';

class VoiceService extends GetxService {
  final _record = Record();
  bool _isRecording = false;

  Future<VoiceService> init() async {
    return this;
  }

  Future<void> startRecording() async {
    try {
      if (await _record.hasPermission()) {
        await _record.start();
        _isRecording = true;
      }
    } catch (e) {
      print('Error starting recording: $e');
      rethrow;
    }
  }

  Future<String> stopRecording() async {
    try {
      if (!_isRecording) return '';
      
      final path = await _record.stop();
      _isRecording = false;
      return path ?? '';
    } catch (e) {
      print('Error stopping recording: $e');
      return '';
    }
  }

  Future<String> speechToText(List<int> audioData) async {
    try {
      // TODO: 实现语音转文字
      return '';
    } catch (e) {
      rethrow;
    }
  }

  Future<List<int>> textToSpeech(String text) async {
    try {
      // TODO: 实现文字转语音
      return [];
    } catch (e) {
      rethrow;
    }
  }
} 