class Group {
  final String id;
  final String name;
  final String avatar;
  final String ownerId;
  String? announcement;
  final int memberCount;
  final DateTime createdAt;
  final Map<String, dynamic>? settings;

  Group({
    required this.id,
    required this.name,
    required this.avatar,
    required this.ownerId,
    this.announcement,
    required this.memberCount,
    required this.createdAt,
    this.settings,
  });

  factory Group.empty() => Group(
    id: '',
    name: '',
    avatar: '',
    ownerId: '',
    memberCount: 0,
    createdAt: DateTime.now(),
  );

  Group copyWith({
    String? name,
    String? avatar,
    String? announcement,
    Map<String, dynamic>? settings,
  }) {
    return Group(
      id: id,
      name: name ?? this.name,
      avatar: avatar ?? this.avatar,
      ownerId: ownerId,
      announcement: announcement ?? this.announcement,
      memberCount: memberCount,
      createdAt: createdAt,
      settings: settings ?? this.settings,
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'name': name,
    'avatar': avatar,
    'ownerId': ownerId,
    'announcement': announcement,
    'memberCount': memberCount,
    'createdAt': createdAt.toIso8601String(),
    'settings': settings,
  };

  factory Group.fromJson(Map<String, dynamic> json) => Group(
    id: json['id'],
    name: json['name'],
    avatar: json['avatar'],
    ownerId: json['ownerId'],
    announcement: json['announcement'],
    memberCount: json['memberCount'],
    createdAt: DateTime.parse(json['createdAt']),
    settings: json['settings'],
  );
} 