import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../core/routes/route_paths.dart';

class HomePage extends StatelessWidget {
  const HomePage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('索克生活'),
        actions: [
          BadgedIcon(
            icon: Icons.person,
            badgeCount: unreadCount,
            onTap: () => Get.to(UserProfilePage()),
          ),
          PopupMenuButton<String>(
            onSelected: (value) {
              switch (value) {
                case 'add_friend':
                  Get.to(() => AddFriendPage());
                  break;
                case 'create_group':
                  Get.to(() => CreateGroupPage());
                  break;
                case 'consultation':
                  Get.to(() => ConsultationPage());
                  break;
                case 'scan':
                  Get.to(() => ScannerPage());
                  break;
                case 'payment':
                  Get.to(() => PaymentPage());
                  break;
              }
            },
            itemBuilder: (context) => [
              PopupMenuItem(
                value: 'add_friend',
                child: ListTile(
                  leading: const Icon(Icons.person_add),
                  title: const Text('添加朋友'),
                ),
              ),
              // ... 其他菜单项
            ],
          ),
          PopupMenuButton<String>(
            onSelected: (value) {
              switch (value) {
                case 'member':
                  Get.to(() => MembershipPage());
                  break;
                case 'expert':
                  Get.to(() => ExpertRegistrationPage());
                  break;
              }
            },
            itemBuilder: (context) => [
              PopupMenuItem(
                value: 'member',
                child: ListTile(
                  leading: const Icon(Icons.card_membership),
                  title: const Text('会员注册'),
                ),
              ),
              PopupMenuItem(
                value: 'expert',
                child: ListTile(
                  leading: const Icon(Icons.psychology),
                  title: const Text('专家注册'),
                ),
              ),
            ],
          ),
        ],
      ),
      body: ChatListView(
        items: [
          ChatItem(
            avatar: 'xiaoi.png',
            title: '小艾',
            subtitle: '您的智能健康助手',
            lastMessage: '您好,我是您的AI健康助手',
            lastMessageTime: DateTime.now(),
            onTap: () => Get.to(() => XiaoiChatPage()),
          ),
          // ... 其他聊天项
        ],
      ),
    );
  }
} 