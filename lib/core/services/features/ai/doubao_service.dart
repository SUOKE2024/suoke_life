import 'package:get/get.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../../../core/services/base_service.dart';
import '../../../core/config/ai_config.dart';

class DouBaoService extends BaseService {
  final _isInitialized = false.obs;
  late final http.Client _client;
  
  String get name => '豆包';
  String get description => '基础AI服务';
  String get model => AiConfig.modelIds['xiaoke']!;

  @override
  Future<void> init() async {
    if (_isInitialized.value) {
      return;
    }
    
    try {
      _client = http.Client();
      // 验证API密钥和连接
      await _testConnection();
      _isInitialized.value = true;
    } catch (e) {
      _isInitialized.value = false;
      rethrow;
    }
  }

  @override
  Future<void> dispose() async {
    if (!_isInitialized.value) {
      return;
    }
    
    try {
      _client.close();
      _isInitialized.value = false;
    } catch (e) {
      rethrow;
    }
  }

  Future<String> chat(String input, {String? modelId}) async {
    if (!_isInitialized.value) {
      throw Exception('DouBaoService not initialized');
    }

    try {
      final response = await _client.post(
        Uri.parse('${AiConfig.baseUrl}/chat/completions'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer YOUR_API_KEY',
        },
        body: jsonEncode({
          'model': modelId ?? model,
          'messages': [
            {
              'role': 'system',
              'content': '你是豆包，是由字节跳动开发的 AI 人工智能助手'
            },
            {
              'role': 'user',
              'content': input
            }
          ],
          'stream': false
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['choices'][0]['message']['content'];
      } else {
        throw Exception('Failed to get response: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Chat request failed: $e');
    }
  }

  Future<bool> handleVoiceInput(String audioPath) async {
    if (!_isInitialized.value) {
      throw Exception('DouBaoService not initialized');
    }
    // 实现语音识别逻辑
    // 示例：调用语音识别服务
    // 实际实现中需要根据具体语音识别服务进行调用
    // 例如：return await _voiceRecognitionService.recognize(audioPath);
    return true;
  }

  Future<String?> generateVoiceOutput(String text) async {
    if (!_isInitialized.value) {
      throw Exception('DouBaoService not initialized');
    }
    // 实现语音合成逻辑
    // 示例：调用语音合成服务
    // 实际实现中需要根据具体语音合成服务进行调用
    // 例如：return await _voiceSynthesisService.synthesize(text);
    return null;
  }

  Future<List<double>> getEmbeddings(String text) async {
    if (!_isInitialized.value) {
      throw Exception('DouBaoService not initialized');
    }

    try {
      final response = await _client.post(
        Uri.parse('${AiConfig.baseUrl}/embeddings'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer YOUR_API_KEY',
        },
        body: jsonEncode({
          'model': AiConfig.modelIds['laoke'],
          'input': [text]
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return List<double>.from(data['data'][0]['embedding']);
      } else {
        throw Exception('Failed to get embeddings: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Embeddings request failed: $e');
    }
  }

  Future<void> _testConnection() async {
    try {
      await chat('测试连接');
    } catch (e) {
      throw Exception('Connection test failed: $e');
    }
  }
} 