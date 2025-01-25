import 'package:flutter_test/flutter_test.dart';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';
import 'package:suoke_life_app_app_app/app/core/database/database_service.dart';
import 'package:suoke_life_app_app_app/app/core/database/models/user.dart';
import 'package:suoke_life_app_app_app/app/core/database/repositories/user_repository.dart';
import 'package:suoke_life_app_app_app/app/core/logger/app_logger.dart';

void main() {
  late DatabaseService database;
  late UserRepository userRepository;
  late AppLogger logger;

  setUpAll(() {
    sqfliteFfiInit();
    databaseFactory = databaseFactoryFfi;
  });

  setUp(() async {
    logger = AppLogger();
    database = DatabaseService(logger);
    userRepository = UserRepository(database);
    
    // 确保每个测试都从空数据库开始
    final db = await database.database;
    await db.execute('DELETE FROM users');
    await db.execute('DELETE FROM chat_sessions');
    await db.execute('DELETE FROM messages');
  });

  tearDown(() async {
    await database.close();
  });

  group('DatabaseService', () {
    test('should create database successfully', () async {
      final db = await database.database;
      expect(db, isNotNull);
      expect(db.isOpen, isTrue);
    });

    test('should create tables successfully', () async {
      final db = await database.database;
      final tables = await db.query('sqlite_master', 
        where: 'type = ?', 
        whereArgs: ['table']
      );
      
      expect(tables, isNotEmpty);
      expect(
        tables.map((t) => t['name']).toList(),
        containsAll([
          'users',
          'chat_sessions',
          'messages',
          'health_data',
          'settings',
          'agriculture_data',
          'knowledge_base',
        ]),
      );
    });

    test('should enforce foreign key constraints', () async {
      final db = await database.database;
      
      // 尝试插入带有无效用户ID的聊天会话
      expect(
        () => db.insert('chat_sessions', {
          'id': 'test_session',
          'user_id': 'non_existent_user',
          'title': 'Test Session',
          'type': 'chat',
          'created_at': DateTime.now().millisecondsSinceEpoch,
          'updated_at': DateTime.now().millisecondsSinceEpoch,
        }),
        throwsException,
      );
    });
  });

  group('UserRepository', () {
    test('should create and retrieve user', () async {
      final now = DateTime.now().millisecondsSinceEpoch;
      final user = User(
        id: 'test_user',
        name: 'Test User',
        email: 'test@example.com',
        phone: '1234567890',
        createdAt: now,
        updatedAt: now,
      );

      await userRepository.createUser(user);
      final retrieved = await userRepository.getUserById('test_user');
      
      expect(retrieved, isNotNull);
      expect(retrieved!.id, equals(user.id));
      expect(retrieved.name, equals(user.name));
      expect(retrieved.email, equals(user.email));
      expect(retrieved.phone, equals(user.phone));
    });

    test('should update user', () async {
      final now = DateTime.now().millisecondsSinceEpoch;
      final user = User(
        id: 'test_user',
        name: 'Test User',
        email: 'test@example.com',
        createdAt: now,
        updatedAt: now,
      );

      await userRepository.createUser(user);
      
      final updatedUser = User(
        id: user.id,
        name: 'Updated Name',
        email: user.email,
        avatar: 'new_avatar.jpg',
        createdAt: user.createdAt,
        updatedAt: DateTime.now().millisecondsSinceEpoch,
      );

      await userRepository.updateUser(updatedUser);
      final retrieved = await userRepository.getUserById(user.id);
      
      expect(retrieved, isNotNull);
      expect(retrieved!.name, equals('Updated Name'));
      expect(retrieved.avatar, equals('new_avatar.jpg'));
    });

    test('should delete user and cascade', () async {
      final now = DateTime.now().millisecondsSinceEpoch;
      final user = User(
        id: 'test_user',
        name: 'Test User',
        createdAt: now,
        updatedAt: now,
      );

      await userRepository.createUser(user);
      
      // 创建用户相关的聊天会话
      final db = await database.database;
      await db.insert('chat_sessions', {
        'id': 'test_session',
        'user_id': user.id,
        'title': 'Test Session',
        'type': 'chat',
        'created_at': now,
        'updated_at': now,
      });

      // 删除用户
      await userRepository.deleteUser(user.id);
      
      // 验证用户被删除
      final deletedUser = await userRepository.getUserById(user.id);
      expect(deletedUser, isNull);
      
      // 验证关联的聊天会话也被删除
      final sessions = await db.query('chat_sessions', 
        where: 'user_id = ?', 
        whereArgs: [user.id]
      );
      expect(sessions, isEmpty);
    });

    test('should enforce unique constraints', () async {
      final now = DateTime.now().millisecondsSinceEpoch;
      final user1 = User(
        id: 'user1',
        name: 'User 1',
        email: 'test@example.com',
        createdAt: now,
        updatedAt: now,
      );

      final user2 = User(
        id: 'user2',
        name: 'User 2',
        email: 'test@example.com', // 相同的邮箱
        createdAt: now,
        updatedAt: now,
      );

      await userRepository.createUser(user1);
      expect(
        () => userRepository.createUser(user2),
        throwsException,
      );
    });
  });
} 