class ActiveMember {
  final String userId;
  final String name;
  final String avatar;
  final int messageCount;
  final int replyCount;
  final double activeScore;
  final Map<String, int> messageTypes;

  const ActiveMember({
    required this.userId,
    required this.name,
    required this.avatar,
    required this.messageCount,
    required this.replyCount,
    required this.activeScore,
    required this.messageTypes,
  });

  factory ActiveMember.fromJson(Map<String, dynamic> json) => ActiveMember(
    userId: json['userId'],
    name: json['name'],
    avatar: json['avatar'],
    messageCount: json['messageCount'],
    replyCount: json['replyCount'],
    activeScore: json['activeScore'].toDouble(),
    messageTypes: Map<String, int>.from(json['messageTypes']),
  );

  Map<String, dynamic> toJson() => {
    'userId': userId,
    'name': name,
    'avatar': avatar,
    'messageCount': messageCount,
    'replyCount': replyCount,
    'activeScore': activeScore,
    'messageTypes': messageTypes,
  };
} 