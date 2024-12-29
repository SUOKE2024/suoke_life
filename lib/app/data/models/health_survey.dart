class HealthSurvey {
  final String id;
  final String title;
  final String description;
  final List<Question> questions;
  final DateTime? deadline;
  final String? status;
  final DateTime createdAt;

  HealthSurvey({
    required this.id,
    required this.title,
    required this.description,
    required this.questions,
    this.deadline,
    this.status,
    DateTime? createdAt,
  }) : createdAt = createdAt ?? DateTime.now();

  factory HealthSurvey.fromMap(Map<String, dynamic> map) {
    return HealthSurvey(
      id: map['id'] as String,
      title: map['title'] as String,
      description: map['description'] as String,
      questions: (map['questions'] as List<dynamic>)
          .map((q) => Question.fromMap(q as Map<String, dynamic>))
          .toList(),
      deadline: map['deadline'] != null 
          ? DateTime.fromMillisecondsSinceEpoch(map['deadline'] as int)
          : null,
      status: map['status'] as String?,
      createdAt: DateTime.fromMillisecondsSinceEpoch(map['created_at'] as int),
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'title': title,
      'description': description,
      'questions': questions.map((q) => q.toMap()).toList(),
      'deadline': deadline?.millisecondsSinceEpoch,
      'status': status,
      'created_at': createdAt.millisecondsSinceEpoch,
    };
  }
}

class Question {
  final String id;
  final String content;
  final String type;
  final List<Option>? options;
  final bool required;

  Question({
    required this.id,
    required this.content,
    required this.type,
    this.options,
    this.required = true,
  });

  factory Question.fromMap(Map<String, dynamic> map) {
    return Question(
      id: map['id'] as String,
      content: map['content'] as String,
      type: map['type'] as String,
      options: map['options'] != null
          ? (map['options'] as List<dynamic>)
              .map((o) => Option.fromMap(o as Map<String, dynamic>))
              .toList()
          : null,
      required: map['required'] as bool? ?? true,
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'content': content,
      'type': type,
      'options': options?.map((o) => o.toMap()).toList(),
      'required': required,
    };
  }
}

class Option {
  final String id;
  final String content;
  final int score;

  Option({
    required this.id,
    required this.content,
    required this.score,
  });

  factory Option.fromMap(Map<String, dynamic> map) {
    return Option(
      id: map['id'] as String,
      content: map['content'] as String,
      score: map['score'] as int,
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'content': content,
      'score': score,
    };
  }
} 