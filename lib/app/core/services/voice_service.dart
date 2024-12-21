import 'package:get/get.dart';
import 'package:record/record.dart';
import '../network/api_client.dart';

class VoiceService extends GetxService {
  final ApiClient _apiClient;
  final _recorder = Record();
  
  VoiceService({required ApiClient apiClient}) : _apiClient = apiClient;

  // 开始录音
  Future<void> startRecording() async {
    try {
      if (await _recorder.hasPermission()) {
        await _recorder.start();
      }
    } catch (e) {
      rethrow;
    }
  }

  // 停止录音
  Future<String?> stopRecording() async {
    try {
      final path = await _recorder.stop();
      if (path != null) {
        // 上传录音文件并获取转写文本
        final response = await _apiClient.uploadVoice(path);
        return response['text'];
      }
      return null;
    } catch (e) {
      rethrow;
    }
  }

  // 语音转文字
  Future<String> speechToText(String audioPath) async {
    try {
      final response = await _apiClient.post('/voice/transcribe', data: {
        'audio_path': audioPath,
      });
      return response['text'];
    } catch (e) {
      rethrow;
    }
  }

  // 文字���语音
  Future<String> textToSpeech(String text) async {
    try {
      final response = await _apiClient.post('/voice/synthesize', data: {
        'text': text,
      });
      return response['audio_url'];
    } catch (e) {
      rethrow;
    }
  }
} 