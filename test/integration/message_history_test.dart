import 'package:flutter_test/flutter_test.dart';
import 'package:suoke_life_app_app_app/app/core/database/database_service.dart';
import 'package:suoke_life_app_app_app/app/features/chat/models/message.dart';
import 'package:suoke_life_app_app_app/app/features/chat/services/message_history_service.dart';
import '../helpers/database_helper.dart';
import '../helpers/test_config.dart';

void main() {
  late MessageHistoryService messageHistoryService;
  late DatabaseService databaseService;

  setUpAll(() async {
    await TestConfig.init();
  });

  setUp(() async {
    databaseService = await DatabaseHelper.getTestDatabase();
    messageHistoryService = MessageHistoryService(databaseService);
    await DatabaseHelper.cleanDatabase(databaseService.database);
  });

  tearDown(() async {
    await DatabaseHelper.closeDatabase(databaseService.database);
  });

  group('Message History Service', () {
    test('should save and retrieve messages with pagination', () async {
      final sessionId = 'test_session';
      
      // 创建25条测试消息
      for (var i = 0; i < 25; i++) {
        final message = Message(
          id: 'msg_$i',
          content: 'Message $i',
          senderId: 'user1',
          timestamp: DateTime.now().add(Duration(minutes: i)),
          isRead: true,
        );
        await messageHistoryService.saveMessage(message, sessionId, 'user');
      }

      // 测试第一页
      final page1 = await messageHistoryService.getMessageHistory(sessionId, page: 1, pageSize: 10);
      expect(page1.length, 10);
      expect(page1.first.content, 'Message 24');  // 最新的消息

      // 测试第二页
      final page2 = await messageHistoryService.getMessageHistory(sessionId, page: 2, pageSize: 10);
      expect(page2.length, 10);
      expect(page2.first.content, 'Message 14');

      // 测试总数
      final total = await messageHistoryService.getTotalMessages(sessionId);
      expect(total, 25);
    });

    test('should delete session history', () async {
      final sessionId = 'test_session';
      
      // 保存一些消息
      await messageHistoryService.saveMessage(
        Message(
          id: 'msg_1',
          content: 'Test message',
          senderId: 'user1',
          timestamp: DateTime.now(),
          isRead: true,
        ),
        sessionId,
        'user',
      );

      // 删除会话历史
      await messageHistoryService.deleteSessionHistory(sessionId);

      // 验证消息已被删除
      final messages = await messageHistoryService.getMessageHistory(sessionId);
      expect(messages.isEmpty, true);
    });
  });
} 