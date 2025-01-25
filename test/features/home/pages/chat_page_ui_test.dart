import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:features_home/pages/chat_page.dart';
import 'package:features_home/providers/chat_provider.dart';
import 'package:mockito/mockito.dart';
import 'package:core/services/ai_service.dart';
import 'package:core/services/chat_service.dart';
import 'package:core/services/data_sync_service.dart';
import 'package:core/utils/error_handler.dart';
import 'package:core/models/chat_message.dart';

class MockChatService extends Mock implements ChatService {}

class MockDataSyncService extends Mock implements DataSyncService {}

class MockAIService extends Mock implements AIService {}

class MockErrorHandler extends Mock implements ErrorHandler {}

void main() {
  late MockChatService mockChatService;
  late MockDataSyncService mockDataSyncService;
  late MockAIService mockAIService;
  late MockErrorHandler mockErrorHandler;

  setUp(() {
    mockChatService = MockChatService();
    mockDataSyncService = MockDataSyncService();
    mockAIService = MockAIService();
    mockErrorHandler = MockErrorHandler();
  });

  testWidgets('ChatPage should display messages', (WidgetTester tester) async {
    when(mockChatService.getChatMessages(any)).thenAnswer((_) async => [
          ChatMessage(
              id: '1',
              content: 'test',
              userId: 'test_user',
              createdAt: DateTime.now()),
        ]);

    await tester.pumpWidget(
      MaterialApp(
        home: ChangeNotifierProvider<ChatProvider>(
          create: (_) => ChatProvider(mockChatService, mockDataSyncService),
          child: const ChatPage(),
        ),
      ),
    );

    expect(find.byType(ChatPage), findsOneWidget);
  });
}
