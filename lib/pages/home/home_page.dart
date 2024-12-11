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
          IconButton(
            icon: const Icon(Icons.person_add),
            onPressed: () {
              // TODO: 添加朋友
              Get.snackbar('提示', '添加朋友功能开发中...');
            },
            tooltip: '添加朋友',
          ),
          IconButton(
            icon: const Icon(Icons.group_add),
            onPressed: () {
              // TODO: 发起群聊
              Get.snackbar('提示', '发起群聊功能开发中...');
            },
            tooltip: '发起群聊',
          ),
          IconButton(
            icon: const Icon(Icons.calendar_month),
            onPressed: () {
              // TODO: 预约
              Get.snackbar('提示', '预约功能开发中...');
            },
            tooltip: '预约',
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // AI助手列表
          const _SectionTitle(title: 'AI助手'),
          _buildChatItem(
            icon: Icons.smart_toy,
            title: '小艾',
            subtitle: '您的智能健康助手',
            badge: '在线',
            badgeColor: Colors.green,
            lastMessage: '您好，我是您的AI健康助手',
            timestamp: DateTime.now().subtract(const Duration(minutes: 5)),
            onTap: () => Get.toNamed(RoutePaths.xiaoiChat),
          ),
          _buildChatItem(
            icon: Icons.psychology,
            title: '老克',
            subtitle: '探索城市的向导',
            badge: '在线',
            badgeColor: Colors.green,
            lastMessage: '发现附近有新的宝藏点',
            timestamp: DateTime.now().subtract(const Duration(hours: 1)),
            onTap: () => Get.toNamed(RoutePaths.laokeChat),
          ),
          _buildChatItem(
            icon: Icons.child_care,
            title: '小克',
            subtitle: '儿童健康助手',
            badge: '在线',
            badgeColor: Colors.green,
            lastMessage: '记得按时喝水哦',
            timestamp: DateTime.now().subtract(const Duration(hours: 2)),
            onTap: () => Get.toNamed(RoutePaths.xiaokeChat),
          ),

          const SizedBox(height: 16),
          // 专家列表
          const _SectionTitle(title: '专家咨询'),
          _buildChatItem(
            icon: Icons.medical_services,
            title: '王医生',
            subtitle: '主任医师',
            badge: '在线',
            badgeColor: Colors.green,
            lastMessage: '请问还有其他不适吗？',
            timestamp: DateTime.now().subtract(const Duration(days: 1)),
            onTap: () => Get.toNamed(RoutePaths.expertChat),
          ),
          _buildChatItem(
            icon: Icons.medical_services,
            title: '李医生',
            subtitle: '副主任医师',
            badge: '忙碌',
            badgeColor: Colors.orange,
            lastMessage: '建议您近期复查一下',
            timestamp: DateTime.now().subtract(const Duration(days: 2)),
            onTap: () => Get.toNamed(RoutePaths.expertChat),
          ),

          const SizedBox(height: 16),
          // 群聊列表
          const _SectionTitle(title: '群聊'),
          _buildChatItem(
            icon: Icons.groups,
            title: '健康交流群',
            subtitle: '128人在线',
            badge: '热门',
            badgeColor: Colors.red,
            lastMessage: '[张三] 请问这个症状正常吗？',
            timestamp: DateTime.now().subtract(const Duration(minutes: 30)),
            onTap: () => Get.toNamed(RoutePaths.groupChat),
          ),
          _buildChatItem(
            icon: Icons.meeting_room,
            title: '在线诊室',
            subtitle: '专家在线问诊',
            badge: '进行中',
            badgeColor: Colors.blue,
            lastMessage: '[系统] 王医生已加入诊室',
            timestamp: DateTime.now().subtract(const Duration(minutes: 15)),
            onTap: () => Get.toNamed(RoutePaths.clinicChat),
          ),
        ],
      ),
    );
  }

  Widget _buildChatItem({
    required IconData icon,
    required String title,
    required String subtitle,
    required String badge,
    required Color badgeColor,
    required VoidCallback onTap,
    required String lastMessage,
    required DateTime timestamp,
  }) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: badgeColor.withOpacity(0.1),
          child: Icon(icon, color: badgeColor),
        ),
        title: Row(
          children: [
            Expanded(child: Text(title)),
            Text(
              _formatTimestamp(timestamp),
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey[600],
              ),
            ),
          ],
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(subtitle),
            const SizedBox(height: 4),
            Text(
              lastMessage,
              style: TextStyle(
                color: Colors.grey[600],
                fontSize: 13,
              ),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
          ],
        ),
        trailing: Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: badgeColor.withOpacity(0.1),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Text(
            badge,
            style: TextStyle(
              color: badgeColor,
              fontSize: 12,
            ),
          ),
        ),
        onTap: onTap,
      ),
    );
  }

  String _formatTimestamp(DateTime timestamp) {
    final now = DateTime.now();
    final difference = now.difference(timestamp);

    if (difference.inMinutes < 60) {
      return '${difference.inMinutes}分钟前';
    } else if (difference.inHours < 24) {
      return '${difference.inHours}小时前';
    } else if (difference.inDays < 7) {
      return '${difference.inDays}天前';
    } else {
      return '${timestamp.month}-${timestamp.day}';
    }
  }
}

class _SectionTitle extends StatelessWidget {
  final String title;

  const _SectionTitle({required this.title});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Text(
        title,
        style: const TextStyle(
          fontSize: 16,
          fontWeight: FontWeight.bold,
          color: Colors.grey,
        ),
      ),
    );
  }
} 