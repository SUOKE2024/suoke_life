import 'package:get/get.dart';
import '../../data/models/chat_message.dart';
import '../../services/features/chat/chat_service.dart';

class ChatDetailController extends GetxController {
  final ChatService _chatService;
  final messages = <ChatMessage>[].obs;
  final isLoading = false.obs;

  String get avatar => 'assets/images/default_avatar.png';
  String get name => 'Chat Name';

  ChatDetailController(this._chatService);

  void showAttachmentOptions() {
    // 显示附件选项
  }

  void startVoiceRecording() {
    // 开始语音录制
  }

  Future<void> sendMessage(String content) async {
    try {
      isLoading.value = true;
      await _chatService.sendMessage(content);
      // 更新消息列表
    } finally {
      isLoading.value = false;
    }
  }
} 