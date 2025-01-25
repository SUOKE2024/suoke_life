import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:suoke_life/features/home/lib/chat_page.dart';
import 'package:suoke_life/core/utils/app_localizations.dart';
import 'package:suoke_life/core/services/ai_service.dart';
import 'package:mocktail/mocktail.dart';
import 'package:suoke_life/main.dart';
import 'package:suoke_life/core/services/infrastructure/local_storage_service.dart';
import 'package:provider/provider.dart';
import 'package:suoke_life/core/models/chat_message.dart';
import 'package:suoke_life/core/services/chat_service.dart';
import 'package:suoke_life/core/services/data_sync_service.dart';
import 'package:suoke_life/core/utils/error_handler.dart';
import 'package:suoke_life/features/home/lib/ai_agent_bubble.dart';
import 'package:suoke_life/core/di/injection.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

import 'chat_page_test.mocks.dart';

class MockAiService extends Mock implements AiService {}
class MockLocalStorageService extends Mock implements LocalStorageService {}
class MockChatService extends Mock implements ChatService {}
class MockDataSyncService extends Mock implements DataSyncService {}
class MockErrorHandler extends Mock implements ErrorHandler {}

void main() async {
  await dotenv.load(fileName: ".env");
  configureDependencies();
  late MockChatService mockChatService;
  late MockDataSyncService mockDataSyncService;
  late MockAiService mockAIService;
  late MockLocalStorageService mockLocalStorage;
  late MockErrorHandler mockErrorHandler;

  setUp(() {
    mockChatService = MockChatService();
    mockDataSyncService = MockDataSyncService();
    mockAIService = MockAiService();
    mockLocalStorage = MockLocalStorageService();
    mockErrorHandler = MockErrorHandler();
    getIt.registerSingleton<ChatService>(mockChatService);
    getIt.registerSingleton<DataSyncService>(mockDataSyncService);
    getIt.registerSingleton<AiService>(mockAIService);
    getIt.registerSingleton<LocalStorageService>(mockLocalStorage);
    getIt.registerSingleton<ErrorHandler>(mockErrorHandler);
  });

  testWidgets('ChatPage UI Test', (WidgetTester tester) async {
    when(() => mockChatService.getMessages())
        .thenAnswer((_) async => [
          ChatMessage(text: 'Old Message', isUser: true),
          ChatMessage(text: 'Old AI Response', isUser: false),
        ]);
    when(() => mockDataSyncService.addToList(any))
        .thenAnswer((_) async => Future.value());
    await tester.pumpWidget(
      MaterialApp(
        localizationsDelegates: const [
          AppLocalizations.delegate,
        ],
        supportedLocales: const [
          Locale('en', 'US'),
          Locale('zh', 'CN'),
        ],
        home: ChangeNotifierProvider(
          create: (_) => ChatProvider(mockChatService, mockDataSyncService),
          child: const ChatPage(),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Old Message'), findsOneWidget);
    expect(find.text('Old AI Response'), findsOneWidget);
  });

  testWidgets('AiAgentBubble displays message and AI response', (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: AiAgentBubble(message: 'Hello AI'),
        ),
      ),
    );

    expect(find.text('Hello AI'), findsOneWidget);
    expect(find.text('Thinking...'), findsOneWidget);

    // 等待 AI 响应
    await tester.pumpAndSettle();

    expect(find.textContaining('AI Response: Hello AI'), findsOneWidget);
  });

  group('Chat Page Tests', () {
    // 这里可以添加其他测试
  });
}
