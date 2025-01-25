enum ChatType {
  ai,      // AI助手
  user,    // 普通用户
  expert,  // 专家
  group,   // 群聊
}

class ChatModel {
  final String id;
  final String name;
  final String avatar;
  final String lastMessage;
  final DateTime timestamp;
  final int unreadCount;
  final ChatType type;
  final bool isPinned;
  final bool isMuted;

  const ChatModel({
    required this.id,
    required this.name,
    required this.avatar,
    required this.lastMessage,
    required this.timestamp,
    this.unreadCount = 0,
    required this.type,
    this.isPinned = false,
    this.isMuted = false,
  });

  ChatModel copyWith({
    String? id,
    String? name,
    String? avatar,
    String? lastMessage,
    DateTime? timestamp,
    int? unreadCount,
    ChatType? type,
    bool? isPinned,
    bool? isMuted,
  }) {
    return ChatModel(
      id: id ?? this.id,
      name: name ?? this.name,
      avatar: avatar ?? this.avatar,
      lastMessage: lastMessage ?? this.lastMessage,
      timestamp: timestamp ?? this.timestamp,
      unreadCount: unreadCount ?? this.unreadCount,
      type: type ?? this.type,
      isPinned: isPinned ?? this.isPinned,
      isMuted: isMuted ?? this.isMuted,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'avatar': avatar,
      'lastMessage': lastMessage,
      'timestamp': timestamp.toIso8601String(),
      'unreadCount': unreadCount,
      'type': type.toString(),
      'isPinned': isPinned,
      'isMuted': isMuted,
    };
  }

  factory ChatModel.fromJson(Map<String, dynamic> json) {
    return ChatModel(
      id: json['id'],
      name: json['name'],
      avatar: json['avatar'],
      lastMessage: json['lastMessage'],
      timestamp: DateTime.parse(json['timestamp']),
      unreadCount: json['unreadCount'],
      type: ChatType.values.firstWhere(
        (e) => e.toString() == json['type'],
        orElse: () => ChatType.user,
      ),
      isPinned: json['isPinned'] ?? false,
      isMuted: json['isMuted'] ?? false,
    );
  }
} 