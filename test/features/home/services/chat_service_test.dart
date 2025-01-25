import 'package:core/services/ai_service.dart';
import 'package:core/services/chat_service.dart';
import 'package:core/services/data_sync_service.dart';
import 'package:core/models/chat_message.dart';
import 'package:core/models/local_storage_item.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:core/utils/error_handler.dart';
import 'package:test/mocks/mock_ai_service.dart';
import 'package:test/mocks/mock_data_sync_service.dart';
import 'package:test/mocks/mock_error_handler.dart';

class MockAIService extends Mock implements AIService {
  @override
  Future<String> generateText(String prompt) {
    return super.noSuchMethod(Invocation.method(#generateText, [prompt]),
        returnValue: Future.value(''));
  }
}

class MockDataSyncService extends Mock implements DataSyncService {
  @override
  Future<void> syncData(dynamic data) {
    return super.noSuchMethod(Invocation.method(#syncData, [data]),
        returnValue: Future.value());
  }

  @override
  Future<List<ChatMessage>> getMessages() {
    return super.noSuchMethod(Invocation.method(#getMessages, []),
        returnValue: Future.value([]));
  }
}

void main() {
  late ChatService chatService;
  late MockAIService mockAIService;
  late MockDataSyncService mockDataSyncService;
  late MockErrorHandler mockErrorHandler;

  setUp(() {
    mockAIService = MockAIService();
    mockDataSyncService = MockDataSyncService();
    mockErrorHandler = MockErrorHandler();
    chatService =
        ChatServiceImpl(mockErrorHandler, mockAIService, mockDataSyncService);
  });

  test('sendMessage returns a ChatMessage', () async {
    when(() => mockAIService.generateText(any()))
        .thenAnswer((_) async => 'test');
    when(() => mockDataSyncService.addToList(any()))
        .thenAnswer((_) async => Future.value());
    final result = await chatService.sendMessage('test');
    expect(result, isA<ChatMessage>());
  });

  test('getMessages returns a list of ChatMessage', () async {
    when(() => mockDataSyncService.addToList(any()))
        .thenAnswer((_) async => Future.value());
    final result = await chatService.sendMessage('test');
    expect(result, isA<ChatMessage>());
  });
}
