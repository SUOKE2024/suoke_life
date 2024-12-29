import 'package:get/get.dart';
import '../../../services/features/suoke/suoke_service.dart';
import '../../../data/models/chat_message.dart';

class ChatDetailController extends GetxController {
  final SuokeService suokeService;
  final String roomId;
  final messages = <ChatMessage>[].obs;

  ChatDetailController({
    required this.suokeService,
    required this.roomId,
  });

  @override
  void onInit() {
    super.onInit();
    loadMessages();
  }

  Future<void> loadMessages() async {
    try {
      final result = await suokeService.getMessages(roomId);
      messages.value = result;
    } catch (e) {
      Get.snackbar('错误', '加载消息失败');
    }
  }

  Future<void> sendMessage(String content) async {
    try {
      await suokeService.sendMessage(roomId, content, 'text');
      await loadMessages();
    } catch (e) {
      Get.snackbar('错误', '发送消息失败');
    }
  }

  void startVoiceInput() {
    // TODO: 实现语音输入
  }

  void showAttachmentOptions() {
    Get.bottomSheet(
      Container(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.camera_alt),
              title: const Text('拍照'),
              onTap: () {
                Get.back();
                // TODO: 实现拍照功能
              },
            ),
            ListTile(
              leading: const Icon(Icons.photo_library),
              title: const Text('相册'),
              onTap: () {
                Get.back();
                // TODO: 实现选择图片功能
              },
            ),
            ListTile(
              leading: const Icon(Icons.file_copy),
              title: const Text('文件'),
              onTap: () {
                Get.back();
                // TODO: 实现选择文件功能
              },
            ),
          ],
        ),
      ),
      backgroundColor: Colors.white,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
    );
  }
} 
} 