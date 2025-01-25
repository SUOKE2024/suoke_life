import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:sqflite/sqflite.dart';
import 'package:redis/redis.dart';
import 'package:suoke_life_app_app/features/life/services/life_record_service.dart';
import 'package:suoke_life_app_app/features/life/models/life_record.dart';
import '../../../mocks.mocks.dart';

void main() {
  late LifeRecordService service;
  late MockDatabase mockDatabase;
  late MockRedisCommands mockRedis;

  setUp(() async {
    mockDatabase = MockDatabase();
    mockRedis = MockRedisCommands();
    service = LifeRecordService();
    // 注入mock对象
    service.database = mockDatabase;
    service.redisCommands = mockRedis;
  });

  group('LifeRecordService Tests', () {
    final testRecord = LifeRecord(
      id: '1',
      title: '测试标题',
      content: '测试内容',
      createdAt: DateTime.now(),
      userId: 'test_user',
    );

    test('insertRecord should insert to database and cache', () async {
      when(mockDatabase.insert(
        'life_records',
        any,
        conflictAlgorithm: ConflictAlgorithm.replace,
      )).thenAnswer((_) async => 1);

      when(mockRedis.set(any, any)).thenAnswer((_) async => 'OK');
      when(mockRedis.expire(any, any)).thenAnswer((_) async => 1);

      await service.insertRecord(testRecord);

      verify(mockDatabase.insert(
        'life_records',
        any,
        conflictAlgorithm: ConflictAlgorithm.replace,
      )).called(1);

      verify(mockRedis.set('life_record:${testRecord.id}', any)).called(1);
      verify(mockRedis.expire('life_record:${testRecord.id}', 3600)).called(1);
    });

    test('getRecords should return cached records if available', () async {
      final cachedData = [testRecord.toMap()];
      when(mockRedis.get('user_records:test_user'))
          .thenAnswer((_) async => cachedData);

      final records = await service.getRecords('test_user');

      expect(records.length, 1);
      expect(records.first.id, testRecord.id);
      verifyNever(mockDatabase.query('life_records'));
    });

    test('getRecords should query database if cache miss', () async {
      when(mockRedis.get('user_records:test_user'))
          .thenAnswer((_) async => null);
      when(mockDatabase.query(
        'life_records',
        where: 'user_id = ?',
        whereArgs: ['test_user'],
        orderBy: 'created_at DESC',
      )).thenAnswer((_) async => [testRecord.toMap()]);

      final records = await service.getRecords('test_user');

      expect(records.length, 1);
      expect(records.first.id, testRecord.id);
      verify(mockDatabase.query(
        'life_records',
        where: 'user_id = ?',
        whereArgs: ['test_user'],
        orderBy: 'created_at DESC',
      )).called(1);
    });

    test('deleteRecord should delete from database and clear cache', () async {
      when(mockDatabase.delete(
        'life_records',
        where: 'id = ?',
        whereArgs: ['1'],
      )).thenAnswer((_) async => 1);

      when(mockRedis.del(any)).thenAnswer((_) async => 1);
      when(mockRedis.get('life_record:1'))
          .thenAnswer((_) async => testRecord.toMap());

      await service.deleteRecord('1');

      verify(mockDatabase.delete(
        'life_records',
        where: 'id = ?',
        whereArgs: ['1'],
      )).called(1);

      verify(mockRedis.del('life_record:1')).called(1);
      verify(mockRedis.del('user_records:test_user')).called(1);
    });
  });
}
