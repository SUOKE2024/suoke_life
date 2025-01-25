import 'package:flutter_test/flutter_test.dart';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';
import 'package:suoke_life_app_app_app/app/core/database/database_service.dart';
import '../helpers/database_helper.dart';
import '../helpers/test_config.dart';

void main() {
  late DatabaseService databaseService;
  late Database database;

  setUpAll(() async {
    await TestConfig.init();
  });

  setUp(() async {
    databaseService = await DatabaseHelper.getTestDatabase();
    database = await databaseFactoryFfi.openDatabase(inMemoryDatabasePath);
  });

  tearDown(() async {
    await DatabaseHelper.closeDatabase(database);
  });

  tearDownAll(() async {
    await TestConfig.cleanup();
  });

  group('Messages CRUD operations', () {
    test('should insert and retrieve a message', () async {
      final messageData = {
        'id': '1',
        'content': 'Test message',
        'sender_id': 'user1',
        'timestamp': DateTime.now().millisecondsSinceEpoch,
        'is_read': 0
      };

      final id = await databaseService.insert('messages', messageData);
      expect(id, isNotNull);

      final results = await databaseService.query(
        'SELECT * FROM messages WHERE id = ?',
        ['1']
      );
      expect(results.length, 1);
      expect(results.first['content'], 'Test message');
    });

    test('should update message read status', () async {
      final messageData = {
        'id': '2',
        'content': 'Unread message',
        'sender_id': 'user2',
        'timestamp': DateTime.now().millisecondsSinceEpoch,
        'is_read': 0
      };

      await databaseService.insert('messages', messageData);
      await databaseService.update(
        'messages',
        {'is_read': 1},
        'id = ?',
        ['2']
      );

      final results = await databaseService.query(
        'SELECT * FROM messages WHERE id = ?',
        ['2']
      );
      expect(results.first['is_read'], 1);
    });

    test('should delete message', () async {
      final messageData = {
        'id': '3',
        'content': 'Message to delete',
        'sender_id': 'user3',
        'timestamp': DateTime.now().millisecondsSinceEpoch,
        'is_read': 0
      };

      await databaseService.insert('messages', messageData);
      await databaseService.delete('messages', 'id = ?', ['3']);

      final results = await databaseService.query(
        'SELECT * FROM messages WHERE id = ?',
        ['3']
      );
      expect(results.isEmpty, true);
    });
  });

  group('Database error handling', () {
    test('should handle duplicate primary key', () async {
      final messageData = {
        'id': '4',
        'content': 'Original message',
        'sender_id': 'user4',
        'timestamp': DateTime.now().millisecondsSinceEpoch,
        'is_read': 0
      };

      await databaseService.insert('messages', messageData);
      
      expect(
        () => databaseService.insert('messages', messageData),
        throwsA(isA<DatabaseException>())
      );
    });

    test('should handle invalid SQL query', () async {
      expect(
        () => databaseService.query('INVALID SQL QUERY'),
        throwsA(isA<DatabaseException>())
      );
    });
  });
} 