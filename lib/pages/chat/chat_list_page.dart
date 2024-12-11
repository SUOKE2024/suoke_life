import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../core/routes/route_paths.dart';
import '../../models/chat_item.dart';

class ChatListPage extends StatelessWidget {
  const ChatListPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        actions: [
          // 添加按钮
          PopupMenuButton<String>(
            icon: const Icon(Icons.add_circle_outline),
            offset: const Offset(0, 45),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            itemBuilder: (context) => [
              _buildPopupMenuItem(
                icon: Icons.person_add,
                title: '专家注册',
                value: RoutePaths.expertRegistration,
                description: '审核通过后显示在本页面',
              ),
              _buildPopupMenuItem(
                icon: Icons.group_add,
                title: '发起群聊',
                value: RoutePaths.groupChat,
                description: '创建群聊',
              ),
              _buildPopupMenuItem(
                icon: Icons.calendar_today,
                title: '线上预约',
                value: RoutePaths.consultation,
                description: '预约服务',
              ),
              _buildPopupMenuItem(
                icon: Icons.qr_code_scanner,
                title: '扫一扫',
                value: '/scan',
                description: '扫描二维码',
              ),
              _buildPopupMenuItem(
                icon: Icons.payment,
                title: '收付款',
                value: '/payment',
                description: '扫码收付款',
              ),
            ],
            onSelected: (value) => Get.toNamed(value),
          ),
        ],
      ),
      body: ListView(
        children: [
          // 小艾（置顶）
          _buildChatItem(
            avatar: 'assets/avatars/xiaoi.png',
            name: '小艾',
            lastMessage: '您好，让我来照顾您的健康',
            isAI: true,
            metrics: const {
              'popularity': 98,
              'serviceHours': 2400,
              'responseRate': 99.8,
            },
            onTap: () => Get.toNamed(RoutePaths.xiaoiChat),
          ),
          
          // 其他AI助手和聊天（按活跃度排序）
          _buildChatItem(
            avatar: 'assets/avatars/laoke.png',
            name: '老克',
            lastMessage: '让我们继续探索知识的海洋',
            isAI: true,
            metrics: const {
              'popularity': 95,
              'serviceHours': 2200,
              'responseRate': 99.5,
            },
            onTap: () => Get.toNamed(RoutePaths.laokeChat),
          ),
          _buildChatItem(
            avatar: 'assets/avatars/xiaoke.png',
            name: '小克',
            lastMessage: '您的贴心商务助理',
            isAI: true,
            metrics: const {
              'popularity': 92,
              'serviceHours': 2100,
              'responseRate': 99.3,
            },
            onTap: () => Get.toNamed(RoutePaths.xiaokeChat),
          ),
        ],
      ),
    );
  }

  PopupMenuItem<String> _buildPopupMenuItem({
    required IconData icon,
    required String title,
    required String value,
    required String description,
  }) {
    return PopupMenuItem<String>(
      value: value,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(icon, size: 20),
              const SizedBox(width: 12),
              Text(title),
            ],
          ),
          Padding(
            padding: const EdgeInsets.only(left: 32),
            child: Text(
              description,
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey[600],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildChatItem({
    required String avatar,
    required String name,
    required String lastMessage,
    required bool isAI,
    required Map<String, dynamic> metrics,
    required VoidCallback onTap,
  }) {
    return Dismissible(
      key: Key(name),
      background: Container(
        color: Colors.red,
        alignment: Alignment.centerRight,
        padding: const EdgeInsets.only(right: 16),
        child: const Icon(Icons.delete, color: Colors.white),
      ),
      direction: DismissDirection.endToStart,
      onDismissed: (direction) {
        // TODO: 处理删除逻辑
      },
      child: ListTile(
        leading: Stack(
          children: [
            CircleAvatar(
              backgroundImage: AssetImage(avatar),
              radius: 24,
            ),
            if (isAI)
              Positioned(
                right: 0,
                bottom: 0,
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 2),
                  decoration: BoxDecoration(
                    color: Colors.blue,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Text(
                    'AI',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 8,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ),
          ],
        ),
        title: Row(
          children: [
            Text(
              name,
              style: const TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 16,
              ),
            ),
            const SizedBox(width: 8),
            if (metrics['popularity'] != null)
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 2),
                decoration: BoxDecoration(
                  color: Colors.orange.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  '${metrics['popularity']}%',
                  style: TextStyle(
                    color: Colors.orange[800],
                    fontSize: 10,
                  ),
                ),
              ),
          ],
        ),
        subtitle: Text(
          lastMessage,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: TextStyle(
            color: Colors.grey[600],
            fontSize: 14,
          ),
        ),
        onTap: onTap,
      ),
    );
  }
} 