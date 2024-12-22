class HealthSurvey {
  final String id;
  final String userId;
  final String type;
  final Map<String, dynamic> answers;
  final int score;
  final String result;
  final String? suggestion;
  final DateTime createdAt;

  HealthSurvey({
    required this.id,
    required this.userId,
    required this.type,
    required this.answers,
    required this.score,
    required this.result,
    this.suggestion,
    required this.createdAt,
  });

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'user_id': userId,
      'type': type,
      'answers': answers,
      'score': score,
      'result': result,
      'suggestion': suggestion,
      'created_at': createdAt.toIso8601String(),
    };
  }

  factory HealthSurvey.fromMap(Map<String, dynamic> map) {
    return HealthSurvey(
      id: map['id'],
      userId: map['user_id'],
      type: map['type'],
      answers: Map<String, dynamic>.from(map['answers']),
      score: map['score'],
      result: map['result'],
      suggestion: map['suggestion'],
      createdAt: DateTime.parse(map['created_at']),
    );
  }
} 