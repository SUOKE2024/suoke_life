import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:suoke_app/app/core/storage/storage_service.dart';

void main() {
  late StorageService storageService;

  setUp(() async {
    SharedPreferences.setMockInitialValues({});
    storageService = StorageService();
    await storageService.init();
  });

  test('should store and retrieve data', () async {
    await storageService.set('test_key', 'test_value');
    final result = await storageService.get<String>('test_key');
    expect(result, 'test_value');
  });

  test('should delete data', () async {
    await storageService.set('test_key', 'test_value');
    await storageService.delete('test_key');
    final result = await storageService.get<String>('test_key');
    expect(result, null);
  });

  test('should clear all data', () async {
    await storageService.set('key1', 'value1');
    await storageService.set('key2', 'value2');
    await storageService.clear();
    final result1 = await storageService.get<String>('key1');
    final result2 = await storageService.get<String>('key2');
    expect(result1, null);
    expect(result2, null);
  });
} 