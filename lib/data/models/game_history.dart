class GameHistory {
  final String id;
  final String gameName;
  final String playTime;
  final int score;
  final DateTime playedAt;

  GameHistory({
    required this.id,
    required this.gameName,
    required this.playTime,
    required this.score,
    required this.playedAt,
  });

  factory GameHistory.fromJson(Map<String, dynamic> json) {
    return GameHistory(
      id: json['id'],
      gameName: json['gameName'],
      playTime: json['playTime'],
      score: json['score'],
      playedAt: DateTime.parse(json['playedAt']),
    );
  }
} 