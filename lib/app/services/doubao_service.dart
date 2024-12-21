import 'package:get/get.dart';
import 'package:dio/dio.dart';
import '../core/config/app_config.dart';

class DoubaoService extends GetxService {
  late final Dio _dio;
  
  @override
  void onInit() {
    super.onInit();
    _initDio();
  }

  void _initDio() {
    _dio = Dio(BaseOptions(
      baseUrl: 'https://api.doubao.com/v1',
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 30),
    ));
  }

  // 调用豆包大模型
  Future<String> chat(String message, {
    String model = 'doubao-pro-32k',
    Map<String, dynamic>? context,
  }) async {
    try {
      final response = await _dio.post('/chat/completions', data: {
        'model': model,
        'messages': [
          {'role': 'user', 'content': message}
        ],
        'context': context,
      });
      
      return response.data['choices'][0]['message']['content'];
    } catch (e) {
      rethrow;
    }
  }

  // 获取文本向量
  Future<List<double>> getEmbeddings(String text) async {
    try {
      final response = await _dio.post('/embeddings', data: {
        'model': 'doubao-embedding',
        'input': text,
      });
      
      return List<double>.from(response.data['data'][0]['embedding']);
    } catch (e) {
      rethrow;
    }
  }
} 