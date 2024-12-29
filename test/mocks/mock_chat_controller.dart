import 'package:get/get.dart';
import 'package:suoke_app/app/presentation/controllers/chat/chat_controller.dart';
import 'package:suoke_app/app/services/features/suoke/suoke_service.dart';
import 'package:suoke_app/app/data/models/chat_message.dart';

class MockChatController extends ChatController {
  @override
  final SuokeService suokeService;

  MockChatController({required this.suokeService}) : super(suokeService) {
    // 初始化测试数据
    messages.value = [
      ChatMessage(
        id: '1',
        roomId: 'test_room',
        content: 'Test message',
        type: 'text',
        senderId: 'user',
        timestamp: DateTime.now(),
      ),
    ];
  }

  @override
  void onInit() {
    // 不调用 super.onInit() 以避免实际的网络请求
  }

  @override
  Future<void> loadMessages() async {
    // 不执行实际的加载操作
  }

  @override
  Future<void> sendMessage(String content, String type) async {
    // 不执行实际的发送操作
  }
} 