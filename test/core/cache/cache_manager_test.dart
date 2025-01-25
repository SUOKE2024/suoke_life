import 'package:flutter_test/flutter_test.dart';
import 'package:suoke_life_app_app_app/app/core/cache/cache_manager.dart';
import 'package:suoke_life_app_app_app/app/core/storage/storage_service.dart';

void main() {
  late CacheManager cacheManager;
  late StorageService storage;

  setUp(() async {
    storage = StorageServiceImpl();
    await storage.init();
    cacheManager = CacheManager(storage);
  });

  tearDown(() async {
    await cacheManager.clear();
  });

  group('CacheManager', () {
    test('should store and retrieve value from memory cache', () async {
      await cacheManager.set('test_key', 'test_value');
      final value = await cacheManager.get<String>('test_key');
      expect(value, equals('test_value'));
    });

    test('should respect cache expiration', () async {
      await cacheManager.set('test_key', 'test_value');
      
      // 立即获取
      var value = await cacheManager.get<String>(
        'test_key',
        maxAge: const Duration(seconds: 1),
      );
      expect(value, equals('test_value'));

      // 等待缓存过期
      await Future.delayed(const Duration(seconds: 2));
      
      // 再次获取，应该返回 null（因为缓存已过期）
      value = await cacheManager.get<String>(
        'test_key',
        maxAge: const Duration(seconds: 1),
      );
      expect(value, isNull);
    });

    test('should clear both memory and storage cache', () async {
      await cacheManager.set('test_key', 'test_value');
      await cacheManager.clear();
      
      final value = await cacheManager.get<String>('test_key');
      expect(value, isNull);
    });

    test('should handle different value types', () async {
      // String
      await cacheManager.set('string_key', 'string_value');
      expect(await cacheManager.get<String>('string_key'), equals('string_value'));

      // int
      await cacheManager.set('int_key', 42);
      expect(await cacheManager.get<int>('int_key'), equals(42));

      // bool
      await cacheManager.set('bool_key', true);
      expect(await cacheManager.get<bool>('bool_key'), equals(true));

      // double
      await cacheManager.set('double_key', 3.14);
      expect(await cacheManager.get<double>('double_key'), equals(3.14));

      // List<String>
      await cacheManager.set('list_key', ['a', 'b', 'c']);
      expect(
        await cacheManager.get<List<String>>('list_key'),
        equals(['a', 'b', 'c']),
      );
    });

    test('should remove single key', () async {
      await cacheManager.set('key1', 'value1');
      await cacheManager.set('key2', 'value2');
      
      await cacheManager.remove('key1');
      
      expect(await cacheManager.get<String>('key1'), isNull);
      expect(await cacheManager.get<String>('key2'), equals('value2'));
    });

    test('should handle concurrent access', () async {
      // 并发写入
      await Future.wait([
        cacheManager.set('key1', 'value1'),
        cacheManager.set('key2', 'value2'),
        cacheManager.set('key3', 'value3'),
      ]);

      // 并发读取
      final results = await Future.wait([
        cacheManager.get<String>('key1'),
        cacheManager.get<String>('key2'),
        cacheManager.get<String>('key3'),
      ]);

      expect(results, equals(['value1', 'value2', 'value3']));
    });
  });
} 