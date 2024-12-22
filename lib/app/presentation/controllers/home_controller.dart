import 'package:get/get.dart';
import '../../data/models/chat_conversation.dart';
import '../../services/chat_service.dart';
import '../../routes/app_pages.dart';

class HomeController extends GetxController {
  final ChatService _chatService = Get.find();
  final conversations = <ChatConversation>[].obs;

  @override
  void onInit() {
    super.onInit();
    ever(conversations, (_) => print('Conversations updated: ${conversations.length}'));
    _loadConversations();
  }

  Future<void> _loadConversations() async {
    try {
      final list = await _chatService.getConversations();
      print('Loaded conversations: ${list.length}');
      conversations.assignAll(list);
    } catch (e) {
      print('Error loading conversations: $e');
    }
  }

  void openChat(ChatConversation conversation) {
    Get.toNamed(
      Routes.CHAT_DETAIL,
      arguments: conversation,
    );
  }

  // 快捷操作方法
  void addFriend() {
    Get.toNamed('/contacts/add');
  }

  void createGroup() {
    Get.toNamed('/chat/create_group');
  }

  void bookConsultation() {
    Get.toNamed('/consultation/book');
  }

  void scanQRCode() {
    Get.toNamed('/scan');
  }

  void showPayment() {
    Get.toNamed('/payment');
  }

  // 注册相关方法
  void registerMember() {
    Get.toNamed('/register/member');
  }

  void registerExpert() {
    Get.toNamed('/register/expert');
  }
} 