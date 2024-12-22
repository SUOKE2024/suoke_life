import 'package:dio/dio.dart';
import 'package:get/get.dart';
import '../core/config/doubao_config.dart';
import '../core/config/env_config.dart';
import '../core/config/assistant_config.dart';

class DouBaoService extends GetxService {
  final _dio = Dio();
  final isTest = false.obs;

  DouBaoService() {
    _dio.options.baseUrl = DouBaoConfig.apiUrl;
    _dio.options.headers = {
      'Authorization': 'Bearer ${DouBaoConfig.apiKey}',
    };
  }

  Future<String> chatWithAssistant(String message, String assistantType) async {
    if (isTest.value) {
      return '这是一个测试回复';
    }

    try {
      // 获取助手配置
      final config = _getAssistantConfig(assistantType);
      
      final response = await _dio.post(
        '/chat/completions',
        data: {
          'model': config['model'],
          'messages': [
            {
              'role': 'system',
              'content': config['prompt'],
            },
            {
              'role': 'user',
              'content': message,
            }
          ],
        },
      );
      
      return response.data['choices'][0]['message']['content'];
    } catch (e) {
      print('Error calling API: $e');
      return '抱歉，我现在无法回答，请稍后再试';
    }
  }

  Map<String, String> _getAssistantConfig(String assistantType) {
    switch (assistantType) {
      case 'xiaoai':
        return AssistantConfig.xiaoai;
      case 'laoke':
        return AssistantConfig.laoke;
      case 'xiaoke':
        return AssistantConfig.xiaoke;
      default:
        return AssistantConfig.xiaoai;
    }
  }
} 