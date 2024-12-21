import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../common/badge_icon.dart';
import '../common/action_menu.dart';

class MainAppBar extends StatelessWidget implements PreferredSizeWidget {
  final String title;
  final int unreadCount;
  final VoidCallback onNotificationTap;
  final VoidCallback onAddTap;
  final VoidCallback onRegisterTap;

  const MainAppBar({
    Key? key,
    required this.title,
    this.unreadCount = 0,
    required this.onNotificationTap,
    required this.onAddTap,
    required this.onRegisterTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return AppBar(
      title: Text(title),
      actions: [
        // 未读消息图标
        IconButton(
          icon: BadgeIcon(
            icon: Icons.notifications_outlined,
            count: unreadCount,
          ),
          onPressed: onNotificationTap,
        ),
        // 快捷操作菜单
        IconButton(
          icon: const Icon(Icons.add_circle_outline),
          onPressed: () => _showQuickMenu(context),
        ),
        // 会员/专家注册
        IconButton(
          icon: const Icon(Icons.person_add_outlined),
          onPressed: onRegisterTap,
        ),
      ],
    );
  }

  void _showQuickMenu(BuildContext context) {
    showModalBottomSheet(
      context: context,
      builder: (context) => ActionMenu(
        items: [
          ActionMenuItem(
            icon: Icons.person_add,
            title: '添加朋友',
            onTap: () => Get.toNamed('/contacts/add'),
          ),
          ActionMenuItem(
            icon: Icons.group_add,
            title: '发起群聊',
            onTap: () => Get.toNamed('/chat/group/create'),
          ),
          ActionMenuItem(
            icon: Icons.calendar_today,
            title: '预约咨询',
            onTap: () => Get.toNamed('/consultation/book'),
          ),
          ActionMenuItem(
            icon: Icons.qr_code_scanner,
            title: '扫一扫',
            onTap: () => Get.toNamed('/scan'),
          ),
          ActionMenuItem(
            icon: Icons.payment,
            title: '收付款',
            onTap: () => Get.toNamed('/payment'),
          ),
        ],
      ),
    );
  }

  @override
  Size get preferredSize => const Size.fromHeight(kToolbarHeight);
} 