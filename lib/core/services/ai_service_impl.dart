import 'package:injectable/injectable.dart';
import 'package:suoke_life/core/services/ai_service.dart';
import 'package:suoke_life/core/services/network_service.dart';
import 'package:dio/dio.dart';
import 'dart:convert';

@LazySingleton(as: AIService)
class AiServiceImpl implements AiService {
  final NetworkService _networkService;

  AiServiceImpl(this._networkService);

  @override
  Future<String> generateResponse(String message) async {
    try {
      final response = await _networkService.post(
        '/llm/generate',
        jsonEncode({'prompt': message}),
      );
      if (response != null && response is Map && response.containsKey('response')) {
        return response['response'];
      } else {
        return 'AI response error';
      }
    } on DioException catch (e) {
      print('Error fetching AI response: $e');
      return 'AI response error';
    }
  }
} 