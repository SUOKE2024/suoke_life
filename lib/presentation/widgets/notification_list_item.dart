import 'package:flutter/material.dart';
import '../../service/models/notification.dart';
import 'package:timeago/timeago.dart' as timeago;

class NotificationListItem extends StatelessWidget {
  final NotificationMessage notification;
  final VoidCallback? onTap;
  final VoidCallback? onDismiss;
  final bool showTypeIcon;
  
  const NotificationListItem({
    super.key,
    required this.notification,
    this.onTap,
    this.onDismiss,
    this.showTypeIcon = true,
  });
  
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return Dismissible(
      key: Key(notification.id),
      direction: DismissDirection.endToStart,
      onDismissed: (_) => onDismiss?.call(),
      background: Container(
        color: Colors.red,
        alignment: Alignment.centerRight,
        padding: const EdgeInsets.only(right: 16),
        child: const Icon(
          Icons.delete,
          color: Colors.white,
        ),
      ),
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (showTypeIcon) ...[
                _buildTypeIcon(),
                const SizedBox(width: 16),
              ],
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      notification.title,
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: notification.isRead ? 
                            FontWeight.normal : 
                            FontWeight.bold,
                      ),
                    ),
                    if (notification.body.isNotEmpty) ...[
                      const SizedBox(height: 4),
                      Text(
                        notification.body,
                        style: theme.textTheme.bodyMedium?.copyWith(
                          color: theme.textTheme.bodyMedium?.color?.withOpacity(0.8),
                        ),
                      ),
                    ],
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        Text(
                          timeago.format(notification.timestamp, locale: 'zh'),
                          style: theme.textTheme.bodySmall?.copyWith(
                            color: theme.textTheme.bodySmall?.color?.withOpacity(0.6),
                          ),
                        ),
                        if (!notification.isRead) ...[
                          const SizedBox(width: 8),
                          Container(
                            width: 8,
                            height: 8,
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              color: theme.colorScheme.primary,
                            ),
                          ),
                        ],
                        if (notification.priority.index >= NotificationPriority.high.index) ...[
                          const SizedBox(width: 8),
                          Icon(
                            Icons.priority_high,
                            size: 16,
                            color: notification.priority == NotificationPriority.urgent ? 
                                Colors.red : 
                                Colors.orange,
                          ),
                        ],
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
  
  Widget _buildTypeIcon() {
    IconData icon;
    Color color;
    
    switch (notification.type) {
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