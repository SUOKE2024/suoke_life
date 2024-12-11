import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:suoke_life/app/core/storage/storage_module.dart';

class MockNetworkService extends Mock implements NetworkService {}
class MockAppConfigManager extends Mock implements AppConfigManager {}
class MockServiceLifecycleManager extends Mock implements ServiceLifecycleManager {}

void main() {
  late StorageModule storageModule;
  late MockNetworkService mockNetwork;
  late MockAppConfigManager mockConfig;
  late MockServiceLifecycleManager mockLifecycle;

  setUp(() {
    mockNetwork = MockNetworkService();
    mockConfig = MockAppConfigManager();
    mockLifecycle = MockServiceLifecycleManager();

    // 注入模拟依赖
    DependencyManager.instance.registerLazySingleton<NetworkService>(
      () => mockNetwork,
    );
    DependencyManager.instance.registerLazySingleton<AppConfigManager>(
      () => mockConfig,
    );
    ServiceLifecycleManager.instance = mockLifecycle;

    storageModule = StorageModule();
  });

  tearDown(() async {
    await storageModule.onDispose();
    DependencyManager.instance.reset();
  });

  group('StorageModule', () {
    test('should have correct name and version', () {
      expect(storageModule.name, equals('storage'));
      expect(storageModule.version, equals('1.0.0'));
    });

    test('should declare correct dependencies', () {
      expect(
        storageModule.dependencies,
        containsAll(['network', 'core']),
      );
    });

    test('should initialize with default config when no config provided', () async {
      when(mockConfig.getConfig<StorageModuleConfig>('storage'))
          .thenAnswer((_) async => null);

      await storageModule.onInitialize();

      verify(mockConfig.getConfig<StorageModuleConfig>('storage')).called(1);
      expect(storageModule.config, isNotNull);
    });

    test('should initialize with provided config', () async {
      final testConfig = StorageModuleConfig(
        settings: const StorageSettings(),
        providers: const {
          StorageType.file: StorageProviderConfig(
            path: 'test/storage',
            name: 'test_storage',
          ),
        },
      );

      when(mockConfig.getConfig<StorageModuleConfig>('storage'))
          .thenAnswer((_) async => testConfig);

      await storageModule.onInitialize();

      verify(mockConfig.getConfig<StorageModuleConfig>('storage')).called(1);
      expect(storageModule.config, equals(testConfig));
    });

    test('should register services on initialization', () async {
      when(mockConfig.getConfig<StorageModuleConfig>('storage'))
          .thenAnswer((_) async => null);

      await storageModule.onInitialize();

      verify(mockLifecycle.registerService(any)).called(greaterThan(0));
    });

    test('should handle initialization errors', () async {
      when(mockConfig.getConfig<StorageModuleConfig>('storage'))
          .thenThrow(Exception('Test error'));

      expect(
        () => storageModule.onInitialize(),
        throwsA(isA<StorageException>()),
      );
    });

    test('should cleanup on dispose', () async {
      await storageModule.onDispose();
      expect(storageModule.config, isNull);
    });
  });

  group('StorageProviders', () {
    test('should initialize enabled providers only', () async {
      final testConfig = StorageModuleConfig(
        settings: const StorageSettings(),
        providers: {
          StorageType.file: const StorageProviderConfig(
            path: 'test/storage',
            name: 'test_storage',
            enabled: true,
          ),
          StorageType.nas: const StorageProviderConfig(
            path: 'test/nas',
            name: 'test_nas',
            enabled: false,
          ),
        },
      );

      when(mockConfig.getConfig<StorageModuleConfig>('storage'))
          .thenAnswer((_) async => testConfig);

      await storageModule.onInitialize();

      // Verify only file storage was initialized
      verify(mockLifecycle.registerService(any)).called(2); // StorageService + FileStorage
    });

    test('should handle provider initialization errors', () async {
      final testConfig = StorageModuleConfig(
        settings: const StorageSettings(),
        providers: {
          StorageType.file: const StorageProviderConfig(
            path: '/invalid/path',
            name: 'invalid_storage',
            enabled: true,
          ),
        },
      );

      when(mockConfig.getConfig<StorageModuleConfig>('storage'))
          .thenAnswer((_) async => testConfig);

      expect(
        () => storageModule.onInitialize(),
        throwsA(isA<StorageException>()),
      );
    });
  });
} 