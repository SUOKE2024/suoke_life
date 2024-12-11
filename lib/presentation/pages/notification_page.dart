import 'package:flutter/material.dart';
import '../../services/services/notification_service.dart';
import '../widgets/notification_list.dart';

class NotificationPage extends StatefulWidget {
  final NotificationService notificationService;

  const NotificationPage({
    super.key,
    required this.notificationService,
  });

  @override
  State<NotificationPage> createState() => _NotificationPageState();
}

class _NotificationPageState extends State<NotificationPage> {
  final _refreshKey = GlobalKey<RefreshIndicatorState>();
  bool _showUnreadOnly = true;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('通知'),
        actions: [
          IconButton(
            icon: Icon(_showUnreadOnly ? Icons.visibility : Icons.visibility_off),
            onPressed: () {
              setState(() {
                _showUnreadOnly = !_showUnreadOnly;
              });
            },
            tooltip: _showUnreadOnly ? '显示全部' : '只显示未读',
          ),
        ],
      ),
      body: RefreshIndicator(
        key: _refreshKey,
        onRefresh: () async {
          setState(() {});
        },
        child: StreamBuilder(
          stream: widget.notificationService.notificationStream,
          builder: (context, _) {
            final notifications = widget.notificationService.getUnreadNotifications();
            
            if (notifications.isEmpty) {
              return Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(
                      Icons.notifications_none,
                      size: 64,
                      color: Colors.grey,
                    ),
                    const SizedBox(height: 16),
                    Text(
                      _showUnreadOnly ? '没有未读通知' : '没有通知',
                      style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                        color: Colors.grey,
                      ),
                    ),
                  ],
                ),
              );
            }

            return NotificationList(
              notifications: notifications,
              onNotificationTap: (id) async {
                await widget.notificationService.markAsRead(id);
                setState(() {});
              },
            );
          },
        ),
      ),
    );
  }
} 