import 'package:core/models/chat_message.dart';
import 'package:core/services/interfaces/chat_service.dart';
import 'package:core/services/interfaces/data_sync_service.dart';
import 'package:features_home/providers/chat_provider.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';

class MockChatService extends Mock implements ChatService {
  @override
  Future<void> sendMessage(String userId, String content) async {
    return super.noSuchMethod(
      Invocation.method(#sendMessage, [userId, content]),
      returnValue: Future.value(),
    );
  }

  @override
  Future<List<ChatMessage>> getChatMessages(String userId) async {
    return super.noSuchMethod(
      Invocation.method(#getChatMessages, [userId]),
      returnValue: Future.value([]),
    );
  }
}

class MockDataSyncService extends Mock implements DataSyncService {
  @override
  Future<void> addToList(String key, dynamic item) async {
    return super.noSuchMethod(
      Invocation.method(#addToList, [key, item]),
      returnValue: Future.value(),
    );
  }

  @override
  Future<List<dynamic>> getList(String key) async {
    return super.noSuchMethod(
      Invocation.method(#getList, [key]),
      returnValue: Future.value([]),
    );
  }
}

void main() {
  late ChatProvider chatProvider;
  late MockChatService mockChatService;
  late MockDataSyncService mockDataSyncService;

  setUp(() {
    mockChatService = MockChatService();
    mockDataSyncService = MockDataSyncService();
    chatProvider = ChatProvider(mockChatService, mockDataSyncService);
  });

  test('sendMessage should call chatService and dataSyncService', () async {
    when(mockChatService.sendMessage(any, any)).thenAnswer((_) async {});
    when(mockDataSyncService.addToList(any, any)).thenAnswer((_) async {});

    await chatProvider.sendMessage('test_user', 'Test Message');

    verify(mockChatService.sendMessage(any, any)).called(1);
    verify(mockDataSyncService.addToList(any, any)).called(1);
  });

  test('getMessages should return messages from dataSyncService', () async {
    when(mockDataSyncService.getList(any)).thenAnswer((_) async => [
          ChatMessage(id: '1', content: 'Test Message 1', userId: 'test_user'),
          ChatMessage(id: '2', content: 'Test Message 2', userId: 'test_user'),
        ]);

    final messages = await chatProvider.getMessages('test_user');

    expect(messages.length, 2);
    expect(messages[0].content, 'Test Message 1');
    expect(messages[1].content, 'Test Message 2');
  });
}
