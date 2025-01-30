class GroupNotification {
  final String id;
  final String groupId;
  final String type; // join_request, member_joined, member_left, role_changed, etc.
  final String content;
  final String senderId;
  final DateTime timestamp;
  final bool isRead;
  final Map<String, dynamic>? metadata;

  const GroupNotification({
    required this.id,
    required this.groupId,
    required this.type,
    required this.content,
    required this.senderId,
    required this.timestamp,
    this.isRead = false,
    this.metadata,
  });

  GroupNotification copyWith({
    bool? isRead,
    Map<String, dynamic>? metadata,
  }) {
    return GroupNotification(
      id: id,
      groupId: groupId,
      type: type,
      content: content,
      senderId: senderId,
      timestamp: timestamp,
      isRead: isRead ?? this.isRead,
      metadata: metadata ?? this.metadata,
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'groupId': groupId,
    'type': type,
    'content': content,
    'senderId': senderId,
    'timestamp': timestamp.toIso8601String(),
    'isRead': isRead,
    'metadata': metadata,
  };

  factory GroupNotification.fromJson(Map<String, dynamic> json) => GroupNotification(
    id: json['id'],
    groupId: json['groupId'],
    type: json['type'],
    content: json['content'],
    senderId: json['senderId'],
    timestamp: DateTime.parse(json['timestamp']),
    isRead: json['isRead'] ?? false,
    metadata: json['metadata'],
  );
} 