class GroupMember {
  final String userId;
  final String name;
  final String avatar;
  final String role; // owner, admin, member
  final DateTime joinedAt;
  final bool isMuted;

  const GroupMember({
    required this.userId,
    required this.name,
    required this.avatar,
    required this.role,
    required this.joinedAt,
    this.isMuted = false,
  });

  GroupMember copyWith({
    String? role,
    bool? isMuted,
  }) {
    return GroupMember(
      userId: userId,
      name: name,
      avatar: avatar,
      role: role ?? this.role,
      joinedAt: joinedAt,
      isMuted: isMuted ?? this.isMuted,
    );
  }

  Map<String, dynamic> toJson() => {
    'userId': userId,
    'name': name,
    'avatar': avatar,
    'role': role,
    'joinedAt': joinedAt.toIso8601String(),
    'isMuted': isMuted,
  };

  factory GroupMember.fromJson(Map<String, dynamic> json) => GroupMember(
    userId: json['userId'],
    name: json['name'],
    avatar: json['avatar'],
    role: json['role'],
    joinedAt: DateTime.parse(json['joinedAt']),
    isMuted: json['isMuted'] ?? false,
  );
} 