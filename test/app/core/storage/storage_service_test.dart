import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:suoke_app/app/core/storage/storage_service.dart';
import '../../../helpers/test_helper.dart';

void main() {
  late StorageService storageService;

  setUpAll(() async {
    await TestHelper.initializeTest();
  });

  setUp(() async {
    SharedPreferences.setMockInitialValues({});
    storageService = StorageService();
    await storageService.init();
  });

  tearDown(() async {
    await storageService.clearLocal();
  });

  group('Storage Service Tests', () {
    test('should save and retrieve sync log', () async {
      const testData = 'test_sync_log';
      await storageService.saveSyncLog(testData);
      
      final result = await storageService.getSyncLog();
      expect(result, equals(testData));
    });
  });
} 