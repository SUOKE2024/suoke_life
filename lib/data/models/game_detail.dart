class GameDetail {
  final String id;
  final String name;
  final String description;
  final String coverUrl;
  final int playerCount;
  final double rating;
  final int averagePlayTime;
  final List<String> tags;
  final DateTime releasedAt;

  GameDetail({
    required this.id,
    required this.name,
    required this.description,
    required this.coverUrl,
    required this.playerCount,
    required this.rating,
    required this.averagePlayTime,
    required this.tags,
    required this.releasedAt,
  });

  factory GameDetail.fromJson(Map<String, dynamic> json) {
    return GameDetail(
      id: json['id'],
      name: json['name'],
      description: json['description'],
      coverUrl: json['coverUrl'],
      playerCount: json['playerCount'],
      rating: json['rating'].toDouble(),
      averagePlayTime: json['averagePlayTime'],
      tags: List<String>.from(json['tags']),
      releasedAt: DateTime.parse(json['releasedAt']),
    );
  }
} 