class GameRanking {
  final String id;
  final String playerName;
  final int score;
  final String lastPlayTime;
  final int rank;

  GameRanking({
    required this.id,
    required this.playerName,
    required this.score,
    required this.lastPlayTime,
    required this.rank,
  });

  factory GameRanking.fromJson(Map<String, dynamic> json) {
    return GameRanking(
      id: json['id'],
      playerName: json['playerName'],
      score: json['score'],
      lastPlayTime: json['lastPlayTime'],
      rank: json['rank'],
    );
  }
} 