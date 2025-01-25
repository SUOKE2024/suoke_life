class LifeActivityData {
  final int? id;
  final String? userId;
  final String? dailyActivities;
  final String? locationHistory;
  final String? taskCompletion;

  LifeActivityData({
    this.id,
    this.userId,
    this.dailyActivities,
    this.locationHistory,
    this.taskCompletion,
  });

  LifeActivityData copyWith({
    int? id,
    String? userId,
    String? dailyActivities,
    String? locationHistory,
    String? taskCompletion,
  }) {
    return LifeActivityData(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      dailyActivities: dailyActivities ?? this.dailyActivities,
      locationHistory: locationHistory ?? this.locationHistory,
      taskCompletion: taskCompletion ?? this.taskCompletion,
    );
  }

  factory LifeActivityData.fromJson(Map<String, dynamic> json) {
    return LifeActivityData(
      id: json['id'],
      userId: json['user_id'],
      dailyActivities: json['daily_activities'],
      locationHistory: json['location_history'],
      taskCompletion: json['task_completion'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'daily_activities': dailyActivities,
      'location_history': locationHistory,
      'task_completion': taskCompletion,
    };
  }
} 