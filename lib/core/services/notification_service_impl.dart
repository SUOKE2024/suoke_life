import 'package:suoke_life/core/services/notification_service.dart';

class NotificationServiceImpl implements NotificationService {
  @override
  Future<void> sendNotification(String message) async {
    // TODO: Implement notification logic
    print('Notification sent: $message');
  }
} 