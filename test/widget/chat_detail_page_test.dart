import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get/get.dart';
import 'package:suoke_app/app/presentation/pages/chat/chat_detail_page.dart';
import 'package:suoke_app/app/presentation/controllers/chat/chat_detail_controller.dart';
import 'package:suoke_app/app/presentation/widgets/chat/message_bubble.dart';
import 'package:suoke_app/app/presentation/widgets/chat/chat_input_bar.dart';
import '../mocks/mock_chat_detail_controller.dart';
import '../mocks/mock_suoke_service.dart';

void main() {
  late MockChatDetailController mockController;
  late MockSuokeService mockSuokeService;

  setUp(() {
    Get.reset();
    mockSuokeService = MockSuokeService();
    mockController = MockChatDetailController(
      roomId: 'test_room',
      suokeService: mockSuokeService,
    );
    Get.put<ChatDetailController>(mockController);
  });

  testWidgets('chat detail page should display correctly', (WidgetTester tester) async {
    await tester.pumpWidget(
      GetMaterialApp(
        home: const ChatDetailPage(),
      ),
    );

    expect(find.byType(MessageBubble), findsWidgets);
    expect(find.byType(ChatInputBar), findsOneWidget);
  });

  tearDown(() {
    Get.reset();
  });
} 