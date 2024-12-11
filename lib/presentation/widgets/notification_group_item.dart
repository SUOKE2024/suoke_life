import 'package:flutter/material.dart';
import '../../service/models/notification_group.dart';
import 'notification_list_item.dart';

class NotificationGroupItem extends StatelessWidget {
  final NotificationGroup group;
  final Function(String) onMessageTap;
  final Function(String) onMessageDismiss;
  final VoidCallback? onMuteToggle;
  final VoidCallback? onMarkAllRead;
  
  const NotificationGroupItem({
    super.key,
    required this.group,
    required this.onMessageTap,
    required this.onMessageDismiss,
    this.onMuteToggle,
    this.onMarkAllRead,
  });
  
  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(
        horizontal: 16,
        vertical: 4,
      ),
      child: Column(
        children: [
          _buildHeader(context),
          if (group.isExpanded) ...[
            const Divider(height: 1),
            _buildMessageList(),
            if (group.messages.isNotEmpty) ...[
              const Divider(height: 1),
              _buildFooter(context),
            ],
          ],
        ],
      ),
    );
  }
  
  Widget _buildHeader(BuildContext context) {
    final theme = Theme.of(context);
    
    return ListTile(
      leading: _buildTypeIcon(),
      title: Text(
        group.title,
        style: theme.textTheme.titleMedium?.copyWith(
          fontWeight: group.unreadCount > 0 ? FontWeight.bold : null,
        ),
      ),
      subtitle: Text(
        '${group.messages.length} 条通知，${group.unreadCount} 条未读',
        style: theme.textTheme.bodySmall?.copyWith(
          color: theme.textTheme.bodySmall?.color?.withOpacity(0.6),
        ),
      ),
      trailing: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (group.unreadCount > 0)
            Container(
              padding: const EdgeInsets.symmetric(
                horizontal: 8,
                vertical: 2,
              ),
              decoration: BoxDecoration(
                color: theme.colorScheme.primary,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                group.unreadCount.toString(),
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onPrimary,
                ),
              ),
            ),
          IconButton(
            icon: Icon(
              group.isMuted ? Icons.notifications_off : Icons.notifications,
              color: group.isMuted ? Colors.grey : null,
            ),
            onPressed: onMuteToggle,
            tooltip: group.isMuted ? '取消静音' : '静音',
          ),
          IconButton(
            icon: Icon(
              group.isExpanded ? Icons.expand_less : Icons.expand_more,
            ),
            onPressed: () {
              group.isExpanded = !group.isExpanded;
              (context as Element).markNeedsBuild();
            },
          ),
        ],
      ),
    );
  }
  
  Widget _buildMessageList() {
    return Column(
      children: group.messages.map((message) {
        return NotificationListItem(
          notification: message,
          onTap: () => onMessageTap(message.id),
          onDismiss: () => onMessageDismiss(message.id),
          showTypeIcon: false,
        );
      }).toList(),
    );
  }
  
  Widget _buildFooter(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(
        horizontal: 16,
        vertical: 8,
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.end,
        children: [
          if (group.unreadCount > 0)
            TextButton.icon(
              icon: const Icon(Icons.check_circle),
              label: const Text('全部已读'),
              onPressed: onMarkAllRead,
            ),
        ],
      ),
    );
  }
  
  Widget _buildTypeIcon() {
    IconData icon;
    Color color;
    
    switch (group.type) {
      case NotificationType.confirmation:
        icon = Icons.check_circle;
        color = Colors.blue;
        break;
      case NotificationType.taskStatus:
        icon = Icons.task_alt;
        color = Colors.green;
        break;
      case NotificationType.systemAlert:
        icon = Icons.warning;
        color = Colors.orange;
        break;
      case NotificationType.userMessage:
        icon = Icons.message;
        color = Colors.purple;
        break;
    }
    
    return Icon(icon, color: color);
  }
} 