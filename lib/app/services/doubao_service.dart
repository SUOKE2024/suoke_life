import 'package:dio/dio.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../core/config/doubao_config.dart';
import '../core/config/env_config.dart';
import 'package:get/get.dart';

class DouBaoService extends GetxService {
  final _dio = Dio(BaseOptions(
    baseUrl: DouBaoConfig.baseUrl,
    headers: {
      'Authorization': 'Bearer ${DouBaoConfig.apiKey}',
      'Content-Type': 'application/json',
    },
  ));

  // 不需要异步初始化
  DouBaoService() {
    print('DouBaoService initialized');
  }

  Future<String> chat(String message, String assistantType) async {
    try {
      final response = await _dio.post(
        '/chat/completions',
        data: {
          'model': DouBaoConfig.assistants[assistantType],
          'messages': [
            {
              'role': 'system',
              'content': DouBaoConfig.systemPrompts[assistantType],
            },
            {
              'role': 'user',
              'content': message,
            },
          ],
        },
      );

      return response.data['choices'][0]['message']['content'];
    } catch (e) {
      print('Error calling DouBao API: $e');
      rethrow;
    }
  }

  Future<List<double>> getEmbeddings(String text) async {
    try {
      final response = await _dio.post(
        '/embeddings',
        data: {
          'model': DouBaoConfig.assistants['laoke'],
          'input': [text],
        },
      );

      return List<double>.from(response.data['data'][0]['embedding']);
    } catch (e) {
      print('Error getting embeddings: $e');
      rethrow;
    }
  }

  Future<String> sendMessage(String message, String model) async {
    try {
      String endpoint;
      Map<String, dynamic> data;
      
      switch (model) {
        case 'xiaoai':
          endpoint = '/chat/completions';
          data = {
            'model': EnvConfig.to.doubaoPro32kEp,
            'messages': [
              {
                'role': 'system',
                'content': DouBaoConfig.systemPrompts[model],
              },
              {
                'role': 'user',
                'content': message,
              },
            ],
          };
          break;
        case 'laoke':
          endpoint = '/chat/completions';
          data = {
            'model': EnvConfig.to.doubaoPro128kEp,
            'messages': [
              {
                'role': 'system',
                'content': DouBaoConfig.systemPrompts[model],
              },
              {
                'role': 'user',
                'content': message,
              },
            ],
          };
          break;
        case 'xiaoke':
          endpoint = '/embeddings';
          data = {
            'model': EnvConfig.to.doubaoEmbeddingKey,
            'input': [message],
          };
          break;
        default:
          throw Exception('Unknown model: $model');
      }

      final response = await _dio.post(endpoint, data: data);
      
      if (model == 'xiaoke') {
        // 处理 embeddings 响应
        final embeddings = List<double>.from(response.data['data'][0]['embedding']);
        // TODO: 使用 embeddings 进行相似度搜索等操作
        return '这是小克的回复...';
      } else {
        // 处理普通聊天响应
        return response.data['choices'][0]['message']['content'];
      }
    } catch (e) {
      print('Error calling DouBao API: $e');
      rethrow;
    }
  }
} 