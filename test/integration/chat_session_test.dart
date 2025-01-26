import 'package:flutter_test/flutter_test.dart';
import 'package:suoke_life_app_app_app/app/features/chat/models/chat_session.dart';
import 'package:suoke_life_app_app_app/app/features/chat/services/chat_session_service.dart';
import '../helpers/database_helper.dart';
import '../helpers/test_config.dart';

void main() {
  late ChatSessionService chatSessionService;
  late DatabaseService databaseService;

  setUpAll(() async {
    await TestConfig.init();
  });

  setUp(() async {
    databaseService = await DatabaseHelper.getTestDatabase();
    chatSessionService = ChatSessionService(databaseService);
    await DatabaseHelper.cleanDatabase(databaseService.database);
  });

  tearDown(() async {
    await DatabaseHelper.closeDatabase(databaseService.database);
  });

  group('Chat Session Tests', () {
    test('should create new chat session', () async {
      final session = ChatSession(
        id: '1',
        participantIds: ['user1', 'user2'],
        lastMessage: 'Hello',
        lastMessageTime: DateTime.now(),
        unreadCount: 0,
      );

      await chatSessionService.createSession(session);
      final retrieved = await chatSessionService.getSession(session.id);

      expect(retrieved, isNotNull);
      expect(retrieved!.participantIds, session.participantIds);
      expect(retrieved.lastMessage, session.lastMessage);
    });

    test('should update last message', () async {
      final session = ChatSession(
        id: '2',
        participantIds: ['user1', 'user2'],
        lastMessage: 'Initial message',
        lastMessageTime: DateTime.now(),
        unreadCount: 0,
      );

      await chatSessionService.createSession(session);
      await chatSessionService.updateLastMessage(
        session.id,
        'Updated message',
        DateTime.now(),
      );

      final updated = await chatSessionService.getSession(session.id);
      expect(updated!.lastMessage, 'Updated message');
    });

    test('should increment unread count', () async {
      final session = ChatSession(
        id: '3',
        participantIds: ['user1', 'user2'],
        lastMessage: 'Test message',
        lastMessageTime: DateTime.now(),
        unreadCount: 0,
      );

      await chatSessionService.createSession(session);
      await chatSessionService.incrementUnreadCount(session.id);

      final updated = await chatSessionService.getSession(session.id);
      expect(updated!.unreadCount, 1);
    });

    test('should get sessions by participant', () async {
      const userId = 'user1';

      await chatSessionService.createSession(ChatSession(
        id: '4',
        participantIds: [userId, 'user2'],
        lastMessage: 'Session 1',
        lastMessageTime: DateTime.now(),
        unreadCount: 0,
      ));

      await chatSessionService.createSession(ChatSession(
        id: '5',
        participantIds: [userId, 'user3'],
        lastMessage: 'Session 2',
        lastMessageTime: DateTime.now(),
        unreadCount: 0,
      ));

      final sessions =
          await chatSessionService.getSessionsByParticipant(userId);
      expect(sessions.length, 2);
      expect(sessions.every((s) => s.participantIds.contains(userId)), true);
    });
  });
}
