import 'package:flutter/material.dart';
import '../../services/models/notification.dart';

class NotificationList extends StatelessWidget {
  final List<NotificationMessage> notifications;
  final Function(String) onNotificationTap;

  const NotificationList({
    super.key,
    required this.notifications,
    required this.onNotificationTap,
  });

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      itemCount: notifications.length,
      itemBuilder: (context, index) {
        final notification = notifications[index];
        return ListTile(
          title: Text(notification.title),
          subtitle: Text(notification.body),
          trailing: !notification.isRead ? const CircleAvatar(
            radius: 4,
            backgroundColor: Colors.red,
          ) : null,
          onTap: () => onNotificationTap(notification.id),
        );
      },
    );
  }
} 