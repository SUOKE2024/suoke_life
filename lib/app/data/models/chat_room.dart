class ChatRoom {
  final String id;
  final String name;
  final String type;  // single, group
  final List<String> participants;
  final DateTime createdAt;

  ChatRoom({
    required this.id,
    required this.name,
    required this.type,
    required this.participants,
    required this.createdAt,
  });

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'name': name,
      'type': type,
      'participants': participants,
      'createdAt': createdAt.toIso8601String(),
    };
  }

  factory ChatRoom.fromMap(Map<String, dynamic> map) {
    return ChatRoom(
      id: map['id'],
      name: map['name'],
      type: map['type'],
      participants: List<String>.from(map['participants']),
      createdAt: DateTime.parse(map['createdAt']),
    );
  }
} 