import 'package:flutter/material.dart';
import 'package:suoke_life/domain/models/agent_model.dart';
import 'package:suoke_life/domain/models/chat_contact_model.dart';
import 'package:intl/intl.dart';

/// 聊天联系人项目组件
class ChatContactItem extends StatelessWidget {
  /// 联系人数据
  final ChatContact contact;
  
  /// 点击回调
  final VoidCallback onTap;
  
  /// 长按回调
  final VoidCallback? onLongPress;

  /// 构造函数
  const ChatContactItem({
    Key? key,
    required this.contact,
    required this.onTap,
    this.onLongPress,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    // 根据联系人类型设置不同的颜色
    Color? avatarBgColor;
    switch (contact.type) {
      case ChatContactType.agent:
        // 根据智能体类型设置不同颜色
        final agentTypeStr = contact.extraData?['agentType'] as String?;
        if (agentTypeStr != null) {
          if (agentTypeStr.contains('xiaoAi')) {
            avatarBgColor = const Color(0xFF35BB78); // 小艾：索克绿
          } else if (agentTypeStr.contains('xiaoKe')) {
            avatarBgColor = const Color(0xFF5E72E4); // 小克：蓝色
          } else if (agentTypeStr.contains('laoKe')) {
            avatarBgColor = const Color(0xFFDA6E2C); // 老克：橙棕色
          } else if (agentTypeStr.contains('suoEr')) {
            avatarBgColor = const Color(0xFFFF6800); // 索儿：索克橙
          }
        }
        break;
      case ChatContactType.doctor:
        avatarBgColor = const Color(0xFF6574F7); // 医生：专业蓝
        break;
      case ChatContactType.provider:
        avatarBgColor = const Color(0xFF4DABF5); // 供应商：鲜亮蓝
        break;
      case ChatContactType.user:
        avatarBgColor = const Color(0xFF9C9FA6); // 用户：灰色
        break;
    }
    
    // 格式化时间
    final dateFormat = DateFormat.Hm(); // 时:分
    final now = DateTime.now();
    final yesterday = DateTime(now.year, now.month, now.day - 1);
    
    String timeText;
    if (contact.lastActiveTime.year == now.year && 
        contact.lastActiveTime.month == now.month && 
        contact.lastActiveTime.day == now.day) {
      // 今天，显示时:分
      timeText = dateFormat.format(contact.lastActiveTime);
    } else if (contact.lastActiveTime.year == yesterday.year && 
               contact.lastActiveTime.month == yesterday.month && 
               contact.lastActiveTime.day == yesterday.day) {
      // 昨天
      timeText = '昨天';
    } else if (now.difference(contact.lastActiveTime).inDays < 7) {
      // 一周内，显示星期几
      final weekdayNames = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];
      final weekday = contact.lastActiveTime.weekday;
      timeText = weekdayNames[weekday - 1];
    } else {
      // 一周前，显示月/日
      timeText = DateFormat.MMMd('zh_CN').format(contact.lastActiveTime);
    }
    
    // 联系人在线状态
    bool isOnline = false;
    if (contact.type == ChatContactType.doctor) {
      isOnline = contact.extraData?['isOnline'] == true;
    }
    
    return ListTile(
      leading: Stack(
        children: [
          CircleAvatar(
            radius: 24,
            backgroundColor: _getBackgroundColor(context, contact.type),
            child: _getContactIcon(contact.type),
          ),
          if (isOnline)
            Positioned(
              right: 0,
              bottom: 0,
              child: Container(
                width: 12,
                height: 12,
                decoration: BoxDecoration(
                  color: Colors.green,
                  shape: BoxShape.circle,
                  border: Border.all(
                    color: Colors.white,
                    width: 2,
                  ),
                ),
              ),
            ),
        ],
      ),
      title: Text(
        contact.name,
        style: theme.textTheme.titleMedium?.copyWith(
          fontWeight: contact.unreadCount > 0 ? FontWeight.bold : FontWeight.normal,
        ),
      ),
      subtitle: Text(
        contact.lastMessage ?? contact.description,
        style: TextStyle(
          color: contact.unreadCount > 0 ? theme.colorScheme.primary : Colors.grey[600],
          fontWeight: contact.unreadCount > 0 ? FontWeight.w500 : FontWeight.normal,
        ),
        maxLines: 1,
        overflow: TextOverflow.ellipsis,
      ),
      trailing: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          Text(
            timeText,
            style: TextStyle(
              fontSize: 12,
              color: contact.unreadCount > 0 ? theme.colorScheme.primary : Colors.grey[500],
            ),
          ),
          const SizedBox(height: 4),
          if (contact.unreadCount > 0)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
              decoration: BoxDecoration(
                color: theme.colorScheme.primary,
                borderRadius: BorderRadius.circular(10),
              ),
              child: Text(
                contact.unreadCount.toString(),
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
        ],
      ),
      onTap: onTap,
      onLongPress: onLongPress,
    );
  }

  /// 获取联系人类型对应的背景颜色
  Color _getBackgroundColor(BuildContext context, ChatContactType type) {
    switch (type) {
      case ChatContactType.agent:
        return Theme.of(context).primaryColor.withOpacity(0.2);
      case ChatContactType.doctor:
        return Colors.blue.withOpacity(0.2);
      case ChatContactType.provider:
        return Colors.orange.withOpacity(0.2);
      case ChatContactType.user:
        return Colors.green.withOpacity(0.2);
    }
  }
  
  /// 获取联系人类型对应的图标
  Widget _getContactIcon(ChatContactType type) {
    switch (type) {
      case ChatContactType.agent:
        return const Icon(Icons.smart_toy, color: Colors.purple);
      case ChatContactType.doctor:
        return const Icon(Icons.medical_services, color: Colors.blue);
      case ChatContactType.provider:
        return const Icon(Icons.store, color: Colors.orange);
      case ChatContactType.user:
        return const Icon(Icons.person, color: Colors.green);
    }
  }
} 