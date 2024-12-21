import 'package:get/get.dart';
import 'package:suoke_life/data/models/chat.dart';

class HomeController extends GetxController {
  // 未读消息总数
  final _unreadCount = 0.obs;
  get unreadCount => _unreadCount;

  // 聊天列表
  final _chatList = <Chat>[].obs;
  get chatList => _chatList;

  @override
  void onInit() {
    super.onInit();
    // 初始化聊天列表
    _chatList.addAll([
      Chat(
        id: '1',
        name: '小艾',
        avatar: 'assets/images/avatars/ai_assistant.png',
        lastMessage: 'AI助手随时为您服务',
        unreadCount: 0,
      ),
      Chat(
        id: '2',
        name: '老克',
        avatar: 'assets/images/avatars/lao_ke.png',
        lastMessage: '发现新的探索任务',
        unreadCount: 2,
      ),
      Chat(
        id: '3',
        name: '小克',
        avatar: 'assets/images/avatars/xiao_ke.png',
        lastMessage: '您有新的生活建议',
        unreadCount: 1,
      ),
    ]);
    
    _updateTotalUnreadCount();
  }

  // 更新总未读数
  void _updateTotalUnreadCount() {
    _unreadCount.value = _chatList.fold(0, (sum, chat) => sum + chat.unreadCount);
  }

  // 用户信息点击
  void onUserInfoTap() {
    Get.toNamed(AppRoutes.USER_PROFILE);
  }

  // 菜单项选择
  void onMenuSelected(String value) {
    switch (value) {
      case 'add_friend':
        Get.toNamed(AppRoutes.ADD_FRIEND);
        break;
      case 'create_group':
        Get.toNamed(AppRoutes.CREATE_GROUP);
        break;
      case 'consultation':
        Get.toNamed(AppRoutes.CONSULTATION);
        break;
      case 'scan':
        Get.toNamed(AppRoutes.SCAN);
        break;
      case 'payment':
        Get.toNamed(AppRoutes.PAYMENT);
        break;
    }
  }

  // 会员注册点击
  void onMembershipTap() {
    Get.toNamed(AppRoutes.MEMBERSHIP);
  }

  // 聊天项点击
  void onChatTap(Chat chat) {
    Get.toNamed(
      AppRoutes.CHAT_DETAIL,
      arguments: {'chatId': chat.id},
    );
  }

  // AI助手点击
  void onAIAssistantTap() {
    Get.toNamed(AppRoutes.AI_CHAT);
  }
} 