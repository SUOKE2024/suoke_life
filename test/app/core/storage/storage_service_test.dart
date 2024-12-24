import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/services.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:suoke_app/app/core/storage/storage_service.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  late StorageService storageService;

  setUp(() async {
    // Set up shared preferences for testing
    SharedPreferences.setMockInitialValues({});
    storageService = StorageService();
    await storageService.init();
  });

  tearDown(() async {
    await storageService.clear();
  });

  test('should save and retrieve sync log', () async {
    const testData = 'test_sync_log';
    await storageService.saveSyncLog(testData);
    
    final result = await storageService.getSyncLog();
    expect(result, equals(testData));
  });
} 