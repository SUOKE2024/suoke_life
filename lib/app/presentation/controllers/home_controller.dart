import 'package:get/get.dart';
import '../../data/models/chat_conversation.dart';
import '../../services/chat_service.dart';

class HomeController extends GetxController {
  final ChatService _chatService = Get.find();
  final conversations = <ChatConversation>[].obs;

  @override
  void onInit() {
    super.onInit();
    loadConversations();
  }

  Future<void> loadConversations() async {
    try {
      final list = await _chatService.getConversations();
      conversations.assignAll(list);
    } catch (e) {
      print('Error loading conversations: $e');
    }
  }

  void openChat(ChatConversation chat) {
    Get.toNamed('/chat', arguments: chat);
  }

  Future<void> createNewChat() async {
    final conversation = await _chatService.createConversation(
      title: '新对话',
      model: 'xiaoai',
      avatar: 'assets/images/xiaoai_avatar.png',
    );
    conversations.insert(0, conversation);
    openChat(conversation);
  }
} 