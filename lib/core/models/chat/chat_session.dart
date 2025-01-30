class ChatSession {
  final String id;
  final List<String> participantIds;
  final String lastMessage;
  final DateTime lastMessageTime;
  final int unreadCount;

  ChatSession({
    required this.id,
    required this.participantIds,
    required this.lastMessage,
    required this.lastMessageTime,
    required this.unreadCount,
  });

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'participant_ids': participantIds.join(','),
      'last_message': lastMessage,
      'last_message_time': lastMessageTime.millisecondsSinceEpoch,
      'unread_count': unreadCount,
    };
  }

  factory ChatSession.fromMap(Map<String, dynamic> map) {
    return ChatSession(
      id: map['id'],
      participantIds: (map['participant_ids'] as String).split(','),
      lastMessage: map['last_message'],
      lastMessageTime: DateTime.fromMillisecondsSinceEpoch(map['last_message_time']),
      unreadCount: map['unread_count'],
    );
  }
} 