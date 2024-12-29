class ChatItem {
  final String avatar;
  final String name;
  final String lastMessage;
  final bool isAI;
  final Map<String, dynamic> metrics;
  final DateTime? lastMessageTime;
  final bool isPinned;

  const ChatItem({
    required this.avatar,
    required this.name,
    required this.lastMessage,
    this.isAI = false,
    this.metrics = const {},
    this.lastMessageTime,
    this.isPinned = false,
  });

  // 用于排序的活跃度得分
  double get activityScore {
    if (!isAI) return 0;
    
    final popularity = metrics['popularity'] as double? ?? 0;
    final serviceHours = metrics['serviceHours'] as double? ?? 0;
    final responseRate = metrics['responseRate'] as double? ?? 0;
    
    // 根据各项指标计算活跃度得分
    return (popularity * 0.4) + (serviceHours / 2400 * 0.3) + (responseRate * 0.3);
  }
} 