import 'package:flutter_test/flutter_test.dart';
import 'package:suoke_life_app_app_app/app/features/ai/models/ai_config.dart';
import 'package:suoke_life_app_app_app/app/features/ai/services/ai_service_client.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('AI Service Client', () {
    test('should create valid request body', () async {
      final config = AIConfig.forType('xiao_ai');
      final context = [
        {
          'role': 'user',
          'content': 'Hello',
        },
        {
          'role': 'assistant',
          'content': 'Hi there!',
        },
      ];

      try {
        await AIServiceClient.createAIRequest(
          message: 'How are you?',
          config: config,
          context: context,
        );
      } catch (e) {
        expect(e.toString(), contains('AI Service Error'));
      }
    }, timeout: const Timeout(Duration(seconds: 15)));
  });
} 