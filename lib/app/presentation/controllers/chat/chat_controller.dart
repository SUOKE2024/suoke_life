import 'package:get/get.dart';
import '../../../services/features/suoke/suoke_service.dart';
import '../../../data/models/chat_message.dart';

class ChatController extends GetxController {
  final SuokeService suokeService;
  final messages = <ChatMessage>[].obs;

  ChatController(this.suokeService);

  @override
  void onInit() {
    super.onInit();
    loadMessages();
  }

  Future<void> loadMessages() async {
    try {
      final result = await suokeService.getMessages('default_room');
      messages.value = result;
    } catch (e) {
      // 处理错误
    }
  }

  Future<void> sendMessage(String content, String type) async {
    try {
      await suokeService.sendMessage('default_room', content, type);
      await loadMessages();
    } catch (e) {
      // 处理错误
    }
  }
} 