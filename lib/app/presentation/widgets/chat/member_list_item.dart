import 'package:flutter/material.dart';
import '../../../data/models/group_member.dart';

class MemberListItem extends StatelessWidget {
  final GroupMember member;
  final bool isOwner;
  final Function(String) onRoleChanged;
  final VoidCallback onRemove;

  const MemberListItem({
    Key? key,
    required this.member,
    required this.isOwner,
    required this.onRoleChanged,
    required this.onRemove,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: CircleAvatar(
        backgroundImage: NetworkImage(member.avatar),
      ),
      title: Row(
        children: [
          Text(member.name),
          const SizedBox(width: 8),
          _buildRoleTag(),
        ],
      ),
      subtitle: Text(member.role == 'owner' ? '群主' : ''),
      trailing: isOwner && member.role != 'owner'
          ? PopupMenuButton<String>(
              onSelected: (value) {
                if (value == 'remove') {
                  onRemove();
                } else {
                  onRoleChanged(value);
                }
              },
              itemBuilder: (context) => [
                const PopupMenuItem(
                  value: 'admin',
                  child: Text('设为管理员'),
                ),
                const PopupMenuItem(
                  value: 'member',
                  child: Text('取消管理员'),
                ),
                const PopupMenuItem(
                  value: 'remove',
                  child: Text('移出群聊'),
                ),
              ],
            )
          : null,
    );
  }

  Widget _buildRoleTag() {
    Color color;
    String text;

    switch (member.role) {
      case 'owner':
        color = Colors.red;
        text = '群主';
        break;
      case 'admin':
        color = Colors.blue;
        text = '管理员';
        break;
      default:
        return const SizedBox();
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(
        text,
        style: TextStyle(
          fontSize: 12,
          color: color,
        ),
      ),
    );
  }
} 