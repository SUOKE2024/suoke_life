import 'package:flutter/material.dart';
import 'package:suoke_life/domain/models/agent_model.dart';
import 'package:suoke_life/domain/models/chat_contact_model.dart';

/// 收藏联系人横向列表组件
class FavoriteContactsRow extends StatelessWidget {
  /// 联系人列表
  final List<ChatContact> contacts;
  
  /// 点击联系人回调
  final Function(ChatContact) onContactTap;

  /// 构造函数
  const FavoriteContactsRow({
    Key? key,
    required this.contacts,
    required this.onContactTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 110,
      padding: const EdgeInsets.symmetric(vertical: 16),
      child: ListView(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        children: [
          ...contacts.map((contact) => _buildFavoriteContactItem(context, contact)),
        ],
      ),
    );
  }
  
  Widget _buildFavoriteContactItem(BuildContext context, ChatContact contact) {
    // 根据联系人类型设置不同的颜色
    Color avatarBgColor;
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
          } else {
            avatarBgColor = Theme.of(context).colorScheme.primary;
          }
        } else {
          avatarBgColor = Theme.of(context).colorScheme.primary;
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
    
    // 判断联系人在线状态
    bool isOnline = false;
    if (contact.type == ChatContactType.doctor) {
      isOnline = contact.extraData?['isOnline'] == true;
    }
    
    return GestureDetector(
      onTap: () => onContactTap(contact),
      child: Container(
        width: 70,
        margin: const EdgeInsets.only(right: 16),
        child: Column(
          children: [
            Stack(
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
                if (contact.unreadCount > 0)
                  Positioned(
                    right: 0,
                    top: 0,
                    child: Container(
                      padding: const EdgeInsets.all(4),
                      decoration: BoxDecoration(
                        color: Theme.of(context).colorScheme.error,
                        shape: BoxShape.circle,
                      ),
                      child: Text(
                        contact.unreadCount.toString(),
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              contact.name,
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 12,
                fontWeight: contact.unreadCount > 0 ? FontWeight.bold : FontWeight.normal,
              ),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
          ],
        ),
      ),
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