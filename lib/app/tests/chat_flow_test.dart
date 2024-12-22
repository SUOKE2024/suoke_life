import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get/get.dart';
import '../data/models/chat_conversation.dart';
import '../presentation/controllers/chat_detail_controller.dart';
import '../services/chat_service.dart';
import '../services/doubao_service.dart';
import '../core/constants/asset_constants.dart';
import './test_env.dart';
import './test_database.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  
  group('聊天流程测试', () {
    late ChatConversation testConversation;
    late ChatDetailController controller;

    setUpAll(() async {
      try {
        // 初始化测试数据库
        await TestDatabase.initTestDatabase();
        
        // 初始化测试环境
        await Get.putAsync(() => TestEnv().init());
        
        // 创建测试会话
        testConversation = ChatConversation(
          id: 1,
          title: '测试会话',
          model: 'xiaoai',
          avatar: AssetConstants.xiaoaiAvatar,
          createdAt: DateTime.now(),
          updatedAt: DateTime.now(),
        );
      } catch (e) {
        print('Setup error: $e');
        rethrow;
      }
    });

    setUp(() async {
      try {
        Get.reset();
        
        // 注入依赖
        final douBaoService = DouBaoService();
        douBaoService.isTest.value = true;
        Get.put<DouBaoService>(douBaoService);
        Get.put<ChatService>(ChatService());
        
        // 创建控制器
        controller = Get.put(ChatDetailController());
      } catch (e) {
        print('Test setup error: $e');
        rethrow;
      }
    });

    testWidgets('发送消息测试', (WidgetTester tester) async {
      try {
        // 构建简单的测试界面
        await tester.pumpWidget(
          MaterialApp(
            home: Material(
              child: Column(
                children: [
                  Expanded(
                    child: Obx(() => ListView.builder(
                      itemCount: controller.messages.length,
                      itemBuilder: (context, index) {
                        final message = controller.messages[index];
                        return ListTile(
                          title: Text(message.content),
                        );
                      },
                    )),
                  ),
                  IconButton(
                    icon: const Icon(Icons.send),
                    onPressed: () => controller.sendMessage('你好'),
                  ),
                ],
              ),
            ),
          ),
        );

        // 等待界面构建完成
        await tester.pumpAndSettle();

        // 点击发送按钮
        await tester.tap(find.byIcon(Icons.send));
        
        // 等待消息处理
        await tester.pump(const Duration(milliseconds: 100));
        await tester.pumpAndSettle();

        // 验证消息
        expect(controller.messages.length, equals(2));
        expect(controller.messages[0].content, equals('你好'));
        expect(controller.messages[1].content, equals('这是一个测试回复'));
      } catch (e) {
        print('Widget test error: $e');
        rethrow;
      }
    });

    test('消息历史记录测试', () async {
      try {
        // 验证初始状态
        expect(controller.messages.length, equals(0));
        
        // 发送消息
        await controller.sendMessage('测试消息');
        
        // 验证消息列表
        expect(controller.messages.length, equals(2));
        expect(controller.messages[0].content, equals('测试消息'));
        expect(controller.messages[1].content, equals('这是一个测试回复'));
      } catch (e) {
        print('Unit test error: $e');
        rethrow;
      }
    });

    tearDown(() {
      try {
        Get.reset();
      } catch (e) {
        print('Teardown error: $e');
      }
    });

    tearDownAll(() {
      try {
        Get.reset();
      } catch (e) {
        print('Final teardown error: $e');
      }
    });
  });
} 