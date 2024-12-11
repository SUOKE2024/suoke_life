import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:suoke_life/app/core/storage/storage_module.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  late StorageModule storageModule;
  late StorageService storageService;

  setUp(() async {
    // Initialize core dependencies
    await DependencyManager.instance.initialize();
    
    // Initialize storage module
    storageModule = StorageModule();
    await storageModule.onInitialize();

    // Get storage service
    storageService = DependencyManager.instance.get<StorageService>();
  });

  tearDown(() async {
    await storageService.clear();
    await storageModule.onDispose();
    await DependencyManager.instance.reset();
  });

  group('Storage Integration', () {
    test('should store and retrieve data across providers', () async {
      // Test file storage
      await storageService.set('test_key', 'test_value', type: StorageType.file);
      final fileValue = await storageService.get<String>('test_key', type: StorageType.file);
      expect(fileValue, equals('test_value'));

      // Test secure storage
      await storageService.set('secure_key', 'secure_value', type: StorageType.secure);
      final secureValue = await storageService.get<String>('secure_key', type: StorageType.secure);
      expect(secureValue, equals('secure_value'));

      // Test cache storage
      await storageService.set('cache_key', 'cache_value', type: StorageType.cache);
      final cacheValue = await storageService.get<String>('cache_key', type: StorageType.cache);
      expect(cacheValue, equals('cache_value'));
    });

    test('should handle complex data types', () async {
      final testData = {
        'name': 'Test User',
        'age': 25,
        'preferences': ['reading', 'gaming'],
      };

      await storageService.set('user_data', testData);
      final retrievedData = await storageService.get<Map<String, dynamic>>('user_data');
      expect(retrievedData, equals(testData));
    });

    test('should respect cache expiration', () async {
      // Set cache with short expiration
      await storageService.set(
        'expiring_key',
        'expiring_value',
        type: StorageType.cache,
        expiration: const Duration(milliseconds: 100),
      );

      // Value should exist initially
      var value = await storageService.get<String>('expiring_key', type: StorageType.cache);
      expect(value, equals('expiring_value'));

      // Wait for expiration
      await Future.delayed(const Duration(milliseconds: 150));

      // Value should be null after expiration
      value = await storageService.get<String>('expiring_key', type: StorageType.cache);
      expect(value, isNull);
    });

    test('should handle concurrent operations', () async {
      // Perform multiple storage operations concurrently
      final futures = List.generate(100, (index) async {
        await storageService.set('key_$index', 'value_$index');
        final value = await storageService.get<String>('key_$index');
        expect(value, equals('value_$index'));
      });

      await Future.wait(futures);
    });

    test('should persist data across module restarts', () async {
      // Store data
      await storageService.set('persistent_key', 'persistent_value');

      // Dispose and reinitialize module
      await storageModule.onDispose();
      await storageModule.onInitialize();

      // Get storage service again
      storageService = DependencyManager.instance.get<StorageService>();

      // Data should still exist
      final value = await storageService.get<String>('persistent_key');
      expect(value, equals('persistent_value'));
    });

    test('should handle network errors with NAS storage', () async {
      // Simulate network error
      NetworkService.instance.simulateError = true;

      expect(
        () => storageService.set('nas_key', 'nas_value', type: StorageType.nas),
        throwsA(isA<StorageException>()),
      );

      NetworkService.instance.simulateError = false;
    });

    test('should handle encryption correctly', () async {
      // Enable encryption in settings
      await StorageConfigLoader.instance.updateConfig(
        StorageModuleConfig(
          settings: const StorageSettings(encryptData: true),
          providers: const {},
        ),
      );

      final sensitiveData = 'sensitive_value';
      await storageService.set('encrypted_key', sensitiveData, type: StorageType.secure);

      // Verify data is encrypted in storage
      final rawData = await SecureStorage.instance.getRaw('encrypted_key');
      expect(rawData, isNot(equals(sensitiveData)));

      // But should decrypt correctly when retrieved
      final decryptedData = await storageService.get<String>('encrypted_key', type: StorageType.secure);
      expect(decryptedData, equals(sensitiveData));
    });
  });
} 