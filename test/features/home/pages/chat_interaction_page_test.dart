import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:provider/provider.dart';
import 'package:suoke_life/core/models/chat_message.dart';
import 'package:suoke_life/core/services/ai_service.dart';
import 'package:suoke_life/core/services/chat_service.dart';
import 'package:suoke_life/core/services/data_sync_service.dart';
import 'package:suoke_life/features/home/lib/chat_interaction_page.dart';
import 'package:suoke_life/features/home/providers/chat_provider.dart';
import 'package:suoke_life/core/services/infrastructure/local_storage_service.dart';
import 'package:suoke_life/core/services/infrastructure/redis_service.dart';
import 'package:suoke_life/core/utils/error_handler.dart';
import 'package:suoke_life/main.dart';

import 'chat_interaction_page_test.mocks.dart';

class MockLocalStorageService extends Mock implements LocalStorageService {}
class MockRedisService extends Mock implements RedisService {}
class MockErrorHandler extends Mock implements ErrorHandler {}
class MockChatService extends Mock implements ChatService {}
class MockDataSyncService extends Mock implements DataSyncService {}
class MockAIService extends Mock implements AiService {}

void main() {
  late MockChatService mockChatService;
  late MockDataSyncService mockDataSyncService;
  late MockAIService mockAIService;
  late MockLocalStorageService mockLocalStorage;
  late MockRedisService mockRedis;
  late MockErrorHandler mockErrorHandler;
  late ChatProvider chatProvider;
  final chatId = 1;

  setUp(() {
    mockChatService = MockChatService();
    mockDataSyncService = MockDataSyncService();
    mockAIService = MockAIService();
    mockLocalStorage = MockLocalStorageService();
    mockRedis = MockRedisService();
    mockErrorHandler = MockErrorHandler();
    getIt.registerSingleton<ChatService>(mockChatService);
    getIt.registerSingleton<DataSyncService>(mockDataSyncService);
    getIt.registerSingleton<AiService>(mockAIService);
    getIt.registerSingleton<LocalStorageService>(mockLocalStorage);
    getIt.registerSingleton<RedisService>(mockRedis);
    getIt.registerSingleton<ErrorHandler>(mockErrorHandler);
    chatProvider = ChatProvider(mockChatService, mockDataSyncService);
  });

  testWidgets('ChatInteractionPage UI Test', (WidgetTester tester) async {
    when(() => mockChatService.getMessages())
        .thenAnswer((_) async => []);
    when(() => mockAIService.generateText(any))
        .thenAnswer((_) async => 'AI Response');
    when(() => mockLocalStorage.insertChat(any, any))
        .thenAnswer((_) async => Future.value());
    when(() => mockRedis.addToCache(any, any))
        .thenAnswer((_) async => Future.value());
    await tester.pumpWidget(
      MaterialApp(
        home: ChangeNotifierProvider<ChatProvider>(
          create: (_) => ChatProvider(mockChatService, mockDataSyncService),
          child: ChatInteractionPage(chatId: chatId),
        ),
      ),
    );

    await tester.enterText(find.byType(TextField), 'Test Message');
    await tester.tap(find.byType(IconButton));
    await tester.pumpAndSettle();

    expect(find.text('AI Response'), findsOneWidget);
  });
}
