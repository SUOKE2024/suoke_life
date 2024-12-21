import 'package:get/get.dart';
import '../../../core/base/base_controller.dart';
import '../../../data/models/chat.dart';

class ChatController extends BaseController {
  final chatList = <Chat>[].obs;
  
  @override
  void initData() {
    _loadChats();
  }
  
  Future<void> _loadChats() async {
    try {
      showLoading();
      // TODO: 从服务器加载聊天列表
      // final chats = await chatService.getChats();
      // chatList.value = chats;
      hideLoading();
    } catch (e) {
      handleError(e);
    }
  }
  
  void searchChats() {
    Get.toNamed(Routes.CHAT_SEARCH);
  }
  
  void openChat(String chatId) {
    Get.toNamed(
      Routes.CHAT_DETAIL,
      arguments: {'chatId': chatId},
    );
  }
  
  void startNewChat() {
    Get.toNamed(Routes.CHAT_NEW);
  }
  
  Future<void> refreshChats() async {
    await _loadChats();
  }
} 