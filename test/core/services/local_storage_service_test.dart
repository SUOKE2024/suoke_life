import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:mockito/mockito.dart';
import 'package:sqflite/sqflite.dart';
import 'package:suoke_life/core/services/infrastructure/local_storage_service.dart';

class MockDatabase extends Mock implements Database {}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  late LocalStorageService localStorageService;
  late MockDatabase mockDatabase;

  setUp(() {
    mockDatabase = MockDatabase();
    GetIt.instance.registerSingleton<Database>(mockDatabase);
    localStorageService = LocalStorageService();
  });

  tearDown(() {
    GetIt.instance.reset();
  });

  group('LocalStorageService', () {
    test('init initializes the database', () async {
      when(mockDatabase.isOpen).thenReturn(true);
      await localStorageService.init();
      expect(localStorageService.isInitialized, true);
    });

    test('insertChat inserts a chat message', () async {
      when(mockDatabase.insert(any, any)).thenAnswer((_) async => 1);
      await localStorageService.init();
      await localStorageService.insertChat('test message', true);
      verify(mockDatabase.insert('chat_history', any)).called(1);
    });

    test('getChats retrieves chat messages', () async {
      when(mockDatabase.query(any)).thenAnswer((_) async => [
        {'id': 1, 'text': 'test message 1', 'isUser': 1},
        {'id': 2, 'text': 'test message 2', 'isUser': 0},
      ]);
      await localStorageService.init();
      final chats = await localStorageService.getChats();
      expect(chats.length, 2);
      expect(chats[0]['text'], 'test message 1');
      expect(chats[1]['isUser'], 0);
    });

    test('clearChatHistory clears all chat messages', () async {
      when(mockDatabase.delete(any)).thenAnswer((_) async => 2);
      await localStorageService.init();
      await localStorageService.clearChatHistory();
      verify(mockDatabase.delete('chat_history')).called(1);
    });
  });
} 