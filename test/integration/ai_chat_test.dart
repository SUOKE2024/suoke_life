import 'package:flutter_test/flutter_test.dart';
import 'package:suoke_life_app_app_app/app/core/database/database_service.dart';
import 'package:suoke_life_app_app_app/app/features/chat/models/chat_session.dart';
import 'package:suoke_life_app_app_app/app/features/chat/services/chat_session_service.dart';
import 'package:suoke_life_app_app_app/app/features/ai/services/ai_chat_service.dart';
import '../helpers/database_helper.dart';
import '../helpers/test_config.dart';

void main() {
  late AIChatService aiChatService;
  late ChatSessionService chatSessionService;
  late DatabaseService databaseService;

  setUpAll(() async {
    await TestConfig.init();
  });

  setUp(() async {
    databaseService = await DatabaseHelper.getTestDatabase();
    chatSessionService = ChatSessionService(databaseService);
    aiChatService = AIChatService(chatSessionService);
    await DatabaseHelper.cleanDatabase(databaseService.database);
  });

  tearDown(() async {
    await DatabaseHelper.closeDatabase(databaseService.database);
  });

  group('AI Chat Integration Tests', () {
    test('should create AI chat session', () async {
      final sessionId = await aiChatService.createAISession('user123', 'xiao_ai');
      final session = await chatSessionService.getSession(sessionId);
      
      expect(session, isNotNull);
      expect(session!.participantIds, contains('xiao_ai'));
      expect(session.participantIds, contains('user123'));
    });

    test('should send message to AI and get response', () async {
      final sessionId = await aiChatService.createAISession('user123', 'lao_ke');
      
      final response = await aiChatService.sendMessage(
        sessionId,
        'user123',
        'Tell me about agricultural products',
      );
      
      expect(response, isNotNull);
      expect(response.content.isNotEmpty, true);
      
      // 验证消息是否被保存到会话中
      final session = await chatSessionService.getSession(sessionId);
      expect(session!.lastMessage, response.content);
    });

    test('should handle different AI assistants', () async {
      // 测试小艾助手
      final xiaoAiSessionId = await aiChatService.createAISession('user123', 'xiao_ai');
      final xiaoAiResponse = await aiChatService.sendMessage(
        xiaoAiSessionId,
        'user123',
        'How can you help me?',
      );
      expect(xiaoAiResponse.aiType, 'xiao_ai');

      // 测试老克助手
      final laoKeSessionId = await aiChatService.createAISession('user123', 'lao_ke');
      final laoKeResponse = await aiChatService.sendMessage(
        laoKeSessionId,
        'user123',
        'Tell me about knowledge exploration',
      );
      expect(laoKeResponse.aiType, 'lao_ke');

      // 测试小克助手
      final xiaoKeSessionId = await aiChatService.createAISession('user123', 'xiao_ke');
      final xiaoKeResponse = await aiChatService.sendMessage(
        xiaoKeSessionId,
        'user123',
        'Help me with business decisions',
      );
      expect(xiaoKeResponse.aiType, 'xiao_ke');
    });

    test('should maintain conversation context', () async {
      final sessionId = await aiChatService.createAISession('user123', 'xiao_ai');
      
      // 发送第一条消息
      await aiChatService.sendMessage(
        sessionId,
        'user123',
        'My name is John',
      );
      
      // 发送后续消息，验证AI是否记住上下文
      final response = await aiChatService.sendMessage(
        sessionId,
        'user123',
        'What is my name?',
      );
      
      expect(response.content.toLowerCase(), contains('john'));
    });
  });
} 