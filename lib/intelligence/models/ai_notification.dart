class AINotification {
  final String id;
  final String userId;
  final String channel;
  final String title;
  final String message;
  final NotificationPriority priority;
  final DateTime timestamp;
  final Map<String, dynamic>? data;
  final Map<String, dynamic>? metadata;

  const AINotification({
    required this.id,
    required this.userId,
    required this.channel,
    required this.title,
    required this.message,
    this.priority = NotificationPriority.normal,
    DateTime? timestamp,
    this.data,
    this.metadata,
  }) : timestamp = timestamp ?? DateTime.now();

  Map<String, dynamic> toMap() => {
    'id': id,
    'user_id': userId,
    'channel': channel,
    'title': title,
    'message': message,
    'priority': priority.toString(),
    'timestamp': timestamp.toIso8601String(),
    'data': data,
    'metadata': metadata,
  };

  factory AINotification.fromMap(Map<String, dynamic> map) => AINotification(
    id: map['id'],
    userId: map['user_id'],
    channel: map['channel'],
    title: map['title'],
    message: map['message'],
    priority: NotificationPriority.values.firstWhere(
      (e) => e.toString() == map['priority'],
      orElse: () => NotificationPriority.normal,
    ),
    timestamp: DateTime.parse(map['timestamp']),
    data: map['data'],
    metadata: map['metadata'],
  );
}

enum NotificationPriority {
  low,
  normal,
  high,
  urgent,
} 