class TcmConstitution {
  final String id;
  final String userId;
  final String type;
  final Map<String, dynamic> analysis;
  final List<String> characteristics;
  final Map<String, List<String>> advice;
  final DateTime createdAt;

  TcmConstitution({
    required this.id,
    required this.userId,
    required this.type,
    required this.analysis,
    required this.characteristics,
    required this.advice,
    required this.createdAt,
  });

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'user_id': userId,
      'type': type,
      'analysis': analysis,
      'characteristics': characteristics,
      'advice': advice,
      'created_at': createdAt.toIso8601String(),
    };
  }

  factory TcmConstitution.fromMap(Map<String, dynamic> map) {
    return TcmConstitution(
      id: map['id'],
      userId: map['user_id'],
      type: map['type'],
      analysis: Map<String, dynamic>.from(map['analysis']),
      characteristics: List<String>.from(map['characteristics']),
      advice: Map<String, List<String>>.from(
        map['advice'].map((key, value) => MapEntry(
          key,
          List<String>.from(value),
        )),
      ),
      createdAt: DateTime.parse(map['created_at']),
    );
  }
} 