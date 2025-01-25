import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:suoke_life_app_app_app/app/core/storage/storage_service.dart';
import '../helpers/test_config.dart';

void main() {
  late StorageService storageService;

  setUpAll(() async {
    await TestConfig.init();
  });

  setUp(() async {
    SharedPreferences.setMockInitialValues({});
    final prefs = await SharedPreferences.getInstance();
    storageService = StorageService(prefs);
  });

  group('Storage operations', () {
    test('should handle different data types', () async {
      // String
      await storageService.write('string_key', 'test_string');
      expect(await storageService.read('string_key'), 'test_string');

      // Integer
      await storageService.write('int_key', 42);
      expect(await storageService.read('int_key'), 42);

      // Boolean
      await storageService.write('bool_key', true);
      expect(await storageService.read('bool_key'), true);

      // Double
      await storageService.write('double_key', 3.14);
      expect(await storageService.read('double_key'), 3.14);

      // List<String>
      await storageService.write('list_key', ['a', 'b', 'c']);
      expect(await storageService.read('list_key'), ['a', 'b', 'c']);
    });

    test('should handle non-existent keys', () async {
      expect(await storageService.read('non_existent'), null);
    });

    test('should clear all data', () async {
      await storageService.write('key1', 'value1');
      await storageService.write('key2', 'value2');
      
      await storageService.clear();
      
      expect(await storageService.read('key1'), null);
      expect(await storageService.read('key2'), null);
    });

    test('should delete specific key', () async {
      await storageService.write('key1', 'value1');
      await storageService.write('key2', 'value2');
      
      await storageService.delete('key1');
      
      expect(await storageService.read('key1'), null);
      expect(await storageService.read('key2'), 'value2');
    });
  });
} 