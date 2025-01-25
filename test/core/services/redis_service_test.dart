import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:redis/redis.dart';
import 'package:suoke_life/core/services/infrastructure/redis_service.dart';

class MockRedisClient extends Mock implements RedisClient {}

void main() {
  late RedisService redisService;
  late MockRedisClient mockRedisClient;

  setUp(() {
    mockRedisClient = MockRedisClient();
    redisService = RedisService();
    redisService.client = mockRedisClient;
  });

  group('RedisService', () {
    test('connect connects to Redis', () async {
      when(mockRedisClient.connect()).thenAnswer((_) async => null);
      await redisService.connect();
      verify(mockRedisClient.connect()).called(1);
    });

    test('set sets a key-value pair', () async {
      when(mockRedisClient.set(any, any)).thenAnswer((_) async => 'OK');
      await redisService.connect();
      final result = await redisService.set('testKey', 'testValue');
      expect(result, 'OK');
      verify(mockRedisClient.set('testKey', 'testValue')).called(1);
    });

    test('get retrieves a value by key', () async {
      when(mockRedisClient.get(any)).thenAnswer((_) async => 'testValue');
      await redisService.connect();
      final result = await redisService.get('testKey');
      expect(result, 'testValue');
      verify(mockRedisClient.get('testKey')).called(1);
    });

    test('delete deletes a key', () async {
      when(mockRedisClient.del(any)).thenAnswer((_) async => 1);
      await redisService.connect();
      final result = await redisService.delete('testKey');
      expect(result, 1);
      verify(mockRedisClient.del('testKey')).called(1);
    });
  });
} 