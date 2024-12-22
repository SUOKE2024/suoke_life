import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/home_controller.dart';
import '../../widgets/chat/chat_list.dart';
import '../../widgets/navigation/custom_bottom_nav_bar.dart';

class HomePage extends GetView<HomeController> {
  const HomePage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('索克生活'),
        actions: [
          // 添加朋友等快捷操作
          IconButton(
            icon: const Icon(Icons.add_circle_outline),
            onPressed: () => _showQuickActions(context),
          ),
          // 会员注册等
          IconButton(
            icon: const Icon(Icons.person_add_outlined),
            onPressed: () => _showRegistrationOptions(context),
          ),
        ],
      ),
      body: Obx(() {
        final conversations = controller.conversations;
        if (conversations.isEmpty) {
          return const Center(
            child: Text('暂无聊天记录'),
          );
        }
        return ChatList(
          conversations: conversations,
          onTap: controller.openChat,
        );
      }),
      bottomNavigationBar: CustomBottomNavBar(
        currentIndex: 0,
        onTap: (index) {
          switch (index) {
            case 1:
              Get.toNamed('/suoke');
              break;
            case 2:
              Get.toNamed('/explore');
              break;
            case 3:
              Get.toNamed('/life');
              break;
            case 4:
              Get.toNamed('/profile');
              break;
          }
        },
      ),
    );
  }

  void _showQuickActions(BuildContext context) {
    showModalBottomSheet(
      context: context,
      builder: (context) => Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          ListTile(
            leading: const Icon(Icons.person_add),
            title: const Text('添加朋友'),
            onTap: () {
              Get.back();
              controller.addFriend();
            },
          ),
          ListTile(
            leading: const Icon(Icons.group_add),
            title: const Text('发起群聊'),
            onTap: () {
              Get.back();
              controller.createGroup();
            },
          ),
          ListTile(
            leading: const Icon(Icons.calendar_today),
            title: const Text('预约咨询'),
            onTap: () {
              Get.back();
              controller.bookConsultation();
            },
          ),
          ListTile(
            leading: const Icon(Icons.qr_code_scanner),
            title: const Text('扫一扫'),
            onTap: () {
              Get.back();
              controller.scanQRCode();
            },
          ),
          ListTile(
            leading: const Icon(Icons.payment),
            title: const Text('收付款'),
            onTap: () {
              Get.back();
              controller.showPayment();
            },
          ),
        ],
      ),
    );
  }

  void _showRegistrationOptions(BuildContext context) {
    showModalBottomSheet(
      context: context,
      builder: (context) => Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          ListTile(
            leading: const Icon(Icons.card_membership),
            title: const Text('会员注册'),
            onTap: () {
              Get.back();
              controller.registerMember();
            },
          ),
          ListTile(
            leading: const Icon(Icons.psychology),
            title: const Text('专家注册'),
            onTap: () {
              Get.back();
              controller.registerExpert();
            },
          ),
        ],
      ),
    );
  }
} 