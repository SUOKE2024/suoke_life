import 'package:dio/dio.dart';
import 'package:get/get.dart';
import '../core/config/doubao_config.dart';
import '../core/config/env_config.dart';
import '../core/config/assistant_config.dart';

class DouBaoService extends GetxService {
  late final Dio _dio;

  @override
  void onInit() {
    super.onInit();
    _dio = Dio(BaseOptions(
      baseUrl: DouBaoConfig.baseUrl,
      headers: {
        'Authorization': 'Bearer ${EnvConfig.to.doubaoApiKey}',
      },
    ));
  }

  Future<String> chat(String message, String model) async {
    try {
      final response = await _dio.post('/chat', data: {
        'message': message,
        'model': model,
      });
      return response.data['response'];
    } catch (e) {
      rethrow;
    }
  }

  Map<String, dynamic> _getAssistantConfig(String type) {
    switch (type) {
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