import 'package:flutter_test/flutter_test.dart';
import 'package:suoke_life/core/services/ai_service.dart';

void main() {
  group('AiService', () {
    test('sendMessage should return a response', () async {
      final aiService = AiService();
      final response = await aiService.sendMessage('Hello');
      expect(response, isNotEmpty);
    });

    test('sendMessage should return a response containing the input message', () async {
      final aiService = AiService();
      final message = 'Test Message';
      final response = await aiService.sendMessage(message);
      expect(response, contains(message));
    });
  });
} 