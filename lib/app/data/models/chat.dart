

class Chat {
  final String id;
  final String type; // 'private', 'group'
  final String title;
  final String? avatar;
  final String? lastMessage;
  final DateTime? lastMessageTime;
  final int unreadCount;
  final bool muted;
  final bool pinned;
  final Map<String, dynamic>? extra;

  Chat({
    required this.id,
    required this.type,
    required this.title,
    this.avatar,
    this.lastMessage,
    this.lastMessageTime,
    this.unreadCount = 0,
    this.muted = false,
    this.pinned = false,
    this.extra,
  });

  factory Chat.fromJson(Map<String, dynamic> json) => _$ChatFromJson(json);
  Map<String, dynamic> toJson() => _$ChatToJson(this);

  Chat copyWith({
    String? id,
    String? type,
    String? title,
    String? avatar,
    String? lastMessage,
    DateTime? lastMessageTime,
    int? unreadCount,
    bool? muted,
    bool? pinned,
    Map<String, dynamic>? extra,
  }) {
    return Chat(
      id: id ?? this.id,
      type: type ?? this.type,
      title: title ?? this.title,
      avatar: avatar ?? this.avatar,
      lastMessage: lastMessage ?? this.lastMessage,
      lastMessageTime: lastMessageTime ?? this.lastMessageTime,
      unreadCount: unreadCount ?? this.unreadCount,
      muted: muted ?? this.muted,
      pinned: pinned ?? this.pinned,
      extra: extra ?? this.extra,
    );
  }
} 