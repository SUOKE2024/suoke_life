class Chat {
  final String id;
  final String name;
  final String avatar;
  final String lastMessage;
  final int unreadCount;

  Chat({
    required this.id,
    required this.name,
    required this.avatar,
    required this.lastMessage,
    this.unreadCount = 0,
  });
} 