import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:suoke_life_app_app_app/app/core/di/injection.dart';
import 'package:suoke_life_app_app_app/app/data/models/chat_message.dart';
import 'package:suoke_life_app_app_app/app/domain/repositories/chat_repository.dart';
import 'package:suoke_app/app/data/repositories/chat_repository_impl.dart';
import 'package:suoke_app/app/presentation/pages/chat/chat_detail_page.dart';
import 'package:suoke_app/app/core/network/network_service.dart';
import 'package:provider/provider.dart';

void main() {
  setUpAll(() {
    configureDependencies();
  });

  late ChatRepository chatRepository;

  setUp(() {
    // 使用真实的实现
    final networkService = NetworkService();
    chatRepository = ChatRepositoryImpl(networkService);
  });

  testWidgets('ChatDetailPage should interact with real AI service', 
      (WidgetTester tester) async {
    // Arrange
    await tester.pumpWidget(
      MaterialApp(
        home: Provider<ChatRepository>(
          create: (_) => chatRepository,
          child: const ChatDetailPage(chatId: 'test-id'),
        ),
      ),
    );
    await tester.pumpAndSettle();

    // Act - 发送消息
    await tester.enterText(find.byType(TextField), '你好，小艾');
    await tester.tap(find.byIcon(Icons.send));
    
    // 等待 AI 响应
    await tester.pumpAndSettle(const Duration(seconds: 5));

    // Assert
    // 验证消息是否显示在界面上
    expect(find.text('你好，小艾'), findsOneWidget);
    
    // 验证是否收到 AI 的回复
    // 注意：这里我们不能验证具体的回复内容，因为 AI 的回复是动态的
    // 但我们可以验证是否有回复消息出现
    expect(find.byType(ChatMessage), findsAtLeast(2)); // 至少有发送的消息和 AI 的回复
  });

  testWidgets('ChatDetailPage should handle continuous conversation', 
      (WidgetTester tester) async {
    // Arrange
    await tester.pumpWidget(
      MaterialApp(
        home: Provider<ChatRepository>(
          create: (_) => chatRepository,
          child: const ChatDetailPage(chatId: 'test-id'),
        ),
      ),
    );
    await tester.pumpAndSettle();

    // Act - 发送多条消息
    final messages = [
      '你好，小艾',
      '今天天气怎么样？',
      '你能帮我做什么？'
    ];

    for (final message in messages) {
      await tester.enterText(find.byType(TextField), message);
      await tester.tap(find.byIcon(Icons.send));
      await tester.pumpAndSettle(const Duration(seconds: 5));
    }

    // Assert
    // 验证所有发送的消息都显示在界面上
    for (final message in messages) {
      expect(find.text(message), findsOneWidget);
    }

    // 验证是否收到对应数量的 AI 回复
    expect(find.byType(ChatMessage), findsAtLeast(messages.length * 2));
  });

  testWidgets('ChatDetailPage should handle long conversations', 
      (WidgetTester tester) async {
    // Arrange
    await tester.pumpWidget(
      MaterialApp(
        home: Provider<ChatRepository>(
          create: (_) => chatRepository,
          child: const ChatDetailPage(chatId: 'test-id'),
        ),
      ),
    );
    await tester.pumpAndSettle();

    // Act - 发送一个较长的对话
    const message = '''
    你好，我想了解一下中医养生的基本原则。
    特别是关于日常饮食和作息方面的建议。
    另外，不同季节是否有不同的养生重点？
    ''';

    await tester.enterText(find.byType(TextField), message);
    await tester.tap(find.byIcon(Icons.send));
    
    // 等待较长时间以获取完整回复
    await tester.pumpAndSettle(const Duration(seconds: 10));

    // Assert
    expect(find.text(message), findsOneWidget);
    expect(find.byType(ChatMessage), findsAtLeast(2));
  });
} 