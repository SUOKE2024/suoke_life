class UserProfile {
  final String id;
  String nickname;
  String? avatar;
  String? bio;
  String? location;
  String? website;
  DateTime? birthday;
  String? gender;
  List<String> interests;
  Map<String, int> gameStats;
  List<String> badges;
  DateTime joinDate;
  DateTime lastActive;

  UserProfile({
    required this.id,
    required this.nickname,
    this.avatar,
    this.bio,
    this.location,
    this.website,
    this.birthday,
    this.gender,
    List<String>? interests,
    Map<String, int>? gameStats,
    List<String>? badges,
    DateTime? joinDate,
    DateTime? lastActive,
  })  : interests = interests ?? [],
        gameStats = gameStats ?? {},
        badges = badges ?? [],
        joinDate = joinDate ?? DateTime.now(),
        lastActive = lastActive ?? DateTime.now();

  // 从JSON创建实例
  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      id: json['id'] as String,
      nickname: json['nickname'] as String,
      avatar: json['avatar'] as String?,
      bio: json['bio'] as String?,
      location: json['location'] as String?,
      website: json['website'] as String?,
      birthday: json['birthday'] != null
          ? DateTime.parse(json['birthday'] as String)
          : null,
      gender: json['gender'] as String?,
      interests: (json['interests'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          [],
      gameStats: (json['game_stats'] as Map<String, dynamic>?)?.map(
            (key, value) => MapEntry(key, value as int),
          ) ??
          {},
      badges:
          (json['badges'] as List<dynamic>?)?.map((e) => e as String).toList() ??
              [],
      joinDate: DateTime.parse(json['join_date'] as String),
      lastActive: DateTime.parse(json['last_active'] as String),
    );
  }

  // 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'nickname': nickname,
      'avatar': avatar,
      'bio': bio,
      'location': location,
      'website': website,
      'birthday': birthday?.toIso8601String(),
      'gender': gender,
      'interests': interests,
      'game_stats': gameStats,
      'badges': badges,
      'join_date': joinDate.toIso8601String(),
      'last_active': lastActive.toIso8601String(),
    };
  }

  // 复制实例并修改部分属性
  UserProfile copyWith({
    String? nickname,
    String? avatar,
    String? bio,
    String? location,
    String? website,
    DateTime? birthday,
    String? gender,
    List<String>? interests,
    Map<String, int>? gameStats,
    List<String>? badges,
    DateTime? lastActive,
  }) {
    return UserProfile(
      id: id,
      nickname: nickname ?? this.nickname,
      avatar: avatar ?? this.avatar,
      bio: bio ?? this.bio,
      location: location ?? this.location,
      website: website ?? this.website,
      birthday: birthday ?? this.birthday,
      gender: gender ?? this.gender,
      interests: interests ?? this.interests,
      gameStats: gameStats ?? this.gameStats,
      badges: badges ?? this.badges,
      joinDate: joinDate,
      lastActive: lastActive ?? this.lastActive,
    );
  }

  // 获取用户等级
  int get level {
    final totalExp = gameStats['experience'] ?? 0;
    return (totalExp / 1000).floor() + 1;
  }

  // 获取等级进度
  double get levelProgress {
    final totalExp = gameStats['experience'] ?? 0;
    return (totalExp % 1000) / 1000;
  }

  // 获取下一级所需经验
  int get expToNextLevel {
    final totalExp = gameStats['experience'] ?? 0;
    return 1000 - (totalExp % 1000);
  }

  // 检查是否拥有某个徽章
  bool hasBadge(String badgeId) {
    return badges.contains(badgeId);
  }

  // 添加徽章
  void addBadge(String badgeId) {
    if (!badges.contains(badgeId)) {
      badges.add(badgeId);
    }
  }

  // 更新游戏统计数据
  void updateGameStats(String key, int value) {
    gameStats[key] = value;
  }

  // 增加游戏统计数据
  void incrementGameStats(String key, [int increment = 1]) {
    gameStats[key] = (gameStats[key] ?? 0) + increment;
  }

  // 添加兴趣标签
  void addInterest(String interest) {
    if (!interests.contains(interest)) {
      interests.add(interest);
    }
  }

  // 移除兴趣标签
  void removeInterest(String interest) {
    interests.remove(interest);
  }

  // 更新最后活跃时间
  void updateLastActive() {
    lastActive = DateTime.now();
  }
} 