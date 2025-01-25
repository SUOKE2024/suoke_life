class ConversationTurn {
  final int? id;
  final String userId;
  final String agentId;
  final int turnIndex;
  final String role;
  final String? text;
  final String? imageUrl;
  final int timestamp; //  使用 int 存储时间戳 (millisecondsSinceEpoch)

  ConversationTurn({
    this.id,
    required this.userId,
    required this.agentId,
    required this.turnIndex,
    required this.role,
    this.text,
    this.imageUrl,
    required this.timestamp, //  使用 int 存储时间戳
  });

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'userId': userId,
      'agentId': agentId,
      'turnIndex': turnIndex,
      'role': role,
      'text': text,
      'imageUrl': imageUrl,
      'timestamp': timestamp, //  将时间戳存储为 int (millisecondsSinceEpoch)
    };
  }

  factory ConversationTurn.fromMap(Map<String, dynamic> map) {
    return ConversationTurn(
      id: map['id'],
      userId: map['userId'],
      agentId: map['agentId'],
      turnIndex: map['turnIndex'],
      role: map['role'],
      text: map['text'],
      imageUrl: map['imageUrl'],
      timestamp: map['timestamp'] as int, //  从 int 读取时间戳
    );
  }

  factory ConversationTurn.fromJson(Map<String, dynamic> json) => ConversationTurn(
    id: json['id'],
    userId: json['userId'],
    agentId: json['agentId'],
    turnIndex: json['turnIndex'],
    role: json['role'],
    text: json['text'] as String?,
    imageUrl: json['imageUrl'] as String?,
    timestamp: json['timestamp'] as int, //  从 int 读取时间戳
  );

  Map<String, dynamic> toJson() => {
    'id': id,
    'userId': userId,
    'agentId': agentId,
    'turnIndex': turnIndex,
    'role': role,
    'text': text,
    'imageUrl': imageUrl,
    'timestamp': timestamp, //  将时间戳存储为 int (millisecondsSinceEpoch)
  };
} 