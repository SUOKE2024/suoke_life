class LeaderboardItem {
  final String userName;
  final int score;
  final String? avatarUrl;
  final String? level;

  LeaderboardItem(
    this.userName,
    this.score, {
    this.avatarUrl,
    this.level,
  });

  factory LeaderboardItem.fromJson(Map<String, dynamic> json) {
    return LeaderboardItem(
      json['userName'] as String,
      json['score'] as int,
      avatarUrl: json['avatarUrl'] as String?,
      level: json['level'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'userName': userName,
      'score': score,
      if (avatarUrl != null) 'avatarUrl': avatarUrl,
      if (level != null) 'level': level,
    };
  }
} 