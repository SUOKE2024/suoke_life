import 'package:flutter_test/flutter_test.dart';
import 'package:dio/dio.dart';
import 'package:suoke_life_app_app_app/app/core/ai/ai_config.dart';
import 'package:suoke_life_app_app_app/app/features/ai/models/ai_service_response.dart';
import 'package:suoke_life_app_app_app/app/features/ai/services/ai_service_client.dart';
import 'package:suoke_life_app_app_app/app/features/ai/services/ai_service.dart';

void main() {
  late AIService aiService;
  late AIConfig aiConfig;

  setUp(() {
    aiConfig = AIConfig(apiKey: const String.fromEnvironment('AI_API_KEY'));
    final client = AIServiceClient(Dio());
    aiService = AIServiceImpl(client, aiConfig);
  });

  group('AI Service Integration Tests', () {
    test('should chat with xiao_ai', () async {
      final response = await aiService.chat(
        message: '你好,请介绍一下你自己',
        modelType: 'xiao_ai',
      );

      expect(response.choices, isNotEmpty);
      expect(response.choices.first.message.content, isNotEmpty);
      print('小艾回复: ${response.choices.first.message.content}');
    }, timeout: const Timeout(Duration(seconds: 30)));

    test('should chat with xiao_ke', () async {
      final response = await aiService.chat(
        message: '常见的十字花科植物有哪些？',
        modelType: 'xiao_ke',
      );

      expect(response.choices, isNotEmpty);
      expect(response.choices.first.message.content, isNotEmpty);
      print('小克回复: ${response.choices.first.message.content}');
    }, timeout: const Timeout(Duration(seconds: 30)));

    test('should generate embeddings with lao_ke', () async {
      final embeddings = await aiService.generateEmbeddings(
        '花椰菜又称菜花、花菜，是一种常见的蔬菜。'
      );

      expect(embeddings, isNotEmpty);
      expect(embeddings.length, equals(1536)); // 检查向量维度
      print('生成的嵌入向量维度: ${embeddings.length}');
    }, timeout: const Timeout(Duration(seconds: 30)));

    test('should check service health', () async {
      final isHealthy = await aiService.checkHealth();
      expect(isHealthy, isTrue);
    });
  });
} 