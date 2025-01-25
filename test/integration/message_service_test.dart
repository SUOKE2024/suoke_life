import 'package:flutter_test/flutter_test.dart';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';
import 'package:suoke_life_app_app_app/app/core/database/database_service.dart';
import 'package:suoke_life_app_app_app/app/features/chat/services/message_service.dart';
import 'package:suoke_life_app_app_app/app/features/chat/models/message.dart';
import '../helpers/database_helper.dart';
import '../helpers/test_config.dart';

void main() {
  late MessageService messageService;
  late DatabaseService databaseService;

  setUpAll(() async {
    await TestConfig.init();
  });

  setUp(() async {
    databaseService = await DatabaseHelper.getTestDatabase();
    messageService = MessageService(databaseService);
    await DatabaseHelper.cleanDatabase(databaseService.database);
  });

  tearDown(() async {
    await DatabaseHelper.closeDatabase(databaseService.database);
  });

  group('Message Service Integration', () {
    test('should save and retrieve message', () async {
      final message = Message(
        id: '1',
        content: 'Hello, World!',
        senderId: 'user1',
        timestamp: DateTime.now(),
        isRead: false,
      );

      await messageService.saveMessage(message);
      final retrieved = await messageService.getMessage(message.id);
      
      expect(retrieved, isNotNull);
      expect(retrieved!.content, message.content);
      expect(retrieved.senderId, message.senderId);
    });

    test('should mark message as read', () async {
      final message = Message(
        id: '2',
        content: 'Unread message',
        senderId: 'user2',
        timestamp: DateTime.now(),
        isRead: false,
      );

      await messageService.saveMessage(message);
      await messageService.markAsRead(message.id);
      
      final updated = await messageService.getMessage(message.id);
      expect(updated!.isRead, true);
    });

    test('should get unread messages count', () async {
      await messageService.saveMessage(Message(
        id: '3',
        content: 'Unread 1',
        senderId: 'user1',
        timestamp: DateTime.now(),
        isRead: false,
      ));

      await messageService.saveMessage(Message(
        id: '4',
        content: 'Unread 2',
        senderId: 'user1',
        timestamp: DateTime.now(),
        isRead: false,
      ));

      final count = await messageService.getUnreadCount('user1');
      expect(count, 2);
    });

    test('should get messages by sender', () async {
      final sender = 'user5';
      await messageService.saveMessage(Message(
        id: '5',
        content: 'Message 1',
        senderId: sender,
        timestamp: DateTime.now(),
        isRead: false,
      ));

      await messageService.saveMessage(Message(
        id: '6',
        content: 'Message 2',
        senderId: sender,
        timestamp: DateTime.now(),
        isRead: false,
      ));

      final messages = await messageService.getMessagesBySender(sender);
      expect(messages.length, 2);
      expect(messages.every((m) => m.senderId == sender), true);
    });
  });

  group('Message Service Error Handling', () {
    test('should handle invalid message id', () async {
      final message = await messageService.getMessage('non_existent');
      expect(message, isNull);
    });

    test('should handle duplicate message save', () async {
      final message = Message(
        id: '7',
        content: 'Duplicate message',
        senderId: 'user7',
        timestamp: DateTime.now(),
        isRead: false,
      );

      await messageService.saveMessage(message);
      expect(
        () => messageService.saveMessage(message),
        throwsA(isA<Exception>()),
      );
    });
  });
} 