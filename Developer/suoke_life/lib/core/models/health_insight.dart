/// 健康洞察数据模型
class HealthInsight {
  /// 用户ID
  final String userId;

  /// 时间戳
  final DateTime timestamp;

  /// 压力水平 (0-1)
  final double stressLevel;

  /// o睡眠质量 (0-1)
  final double sleepQuality;

  /// 活动水平 (0-1)
  final double activityLevel;

  /// 心率变异性 (ms)
  final double heartRateVariability;

  /// 身体平衡指数 (0-100)
  final double bodyBalance;

  /// 恢复指数 (0-100)
  final double recoveryIndex;

  /// 评论内容
  final String comments;

  /// 健康建议
  final List<String> recommendations;

  /// 构造函数
  HealthInsight({
    required this.userId,
    required this.timestamp,
    required this.stressLevel,
    required this.sleepQuality,
    required this.activityLevel,
    required this.heartRateVariability,
    required this.bodyBalance,
    required this.recoveryIndex,
    required this.comments,
    required this.recommendations,
  });

  /// 创建空洞察
  factory HealthInsight.empty() {
    return HealthInsight(
      userId: 'unknown',
      timestamp: DateTime.now(),
      stressLevel: 0.0,
      sleepQuality: 0.0,
      activityLevel: 0.0,
      heartRateVariability: 0.0,
      bodyBalance: 0.0,
      recoveryIndex: 0.0,
      comments: '',
      recommendations: [],
    );
  }

  /// 合并两个洞察结果
  static HealthInsight merge(HealthInsight insight1, HealthInsight insight2) {
    // 使用时间较新的数据
    final useFirst = insight1.timestamp.isAfter(insight2.timestamp);
    final primary = useFirst ? insight1 : insight2;
    final secondary = useFirst ? insight2 : insight1;

    // 合并推荐
    final mergedRecommendations = [...primary.recommendations];
    for (final rec in secondary.recommendations) {
      if (!mergedRecommendations.contains(rec)) {
        mergedRecommendations.add(rec);
      }
    }

    // 限制推荐数量
    if (mergedRecommendations.length > 5) {
      mergedRecommendations.removeRange(5, mergedRecommendations.length);
    }

    return HealthInsight(
      userId: primary.userId,
      timestamp: primary.timestamp,
      stressLevel: primary.stressLevel,
      sleepQuality: primary.sleepQuality,
      activityLevel: primary.activityLevel,
      heartRateVariability: primary.heartRateVariability,
      bodyBalance: primary.bodyBalance,
      recoveryIndex: primary.recoveryIndex,
      comments: primary.comments,
      recommendations: mergedRecommendations,
    );
  }

  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'userId': userId,
      'timestamp': timestamp.toIso8601String(),
      'stressLevel': stressLevel,
      'sleepQuality': sleepQuality,
      'activityLevel': activityLevel,
      'heartRateVariability': heartRateVariability,
      'bodyBalance': bodyBalance,
      'recoveryIndex': recoveryIndex,
      'comments': comments,
      'recommendations': recommendations,
    };
  }

  /// 从JSON创建
  factory HealthInsight.fromJson(Map<String, dynamic> json) {
    return HealthInsight(
      userId: json['userId'] ?? 'unknown',
      timestamp: DateTime.parse(json['timestamp']),
      stressLevel: json['stressLevel'] ?? 0.0,
      sleepQuality: json['sleepQuality'] ?? 0.0,
      activityLevel: json['activityLevel'] ?? 0.0,
      heartRateVariability: json['heartRateVariability'] ?? 0.0,
      bodyBalance: json['bodyBalance'] ?? 0.0,
      recoveryIndex: json['recoveryIndex'] ?? 0.0,
      comments: json['comments'] ?? '',
      recommendations: List<String>.from(json['recommendations'] ?? []),
    );
  }

  /// 获取总健康状况评分 (0-100)
  double getOverallScore() {
    return (stressLevel * 20 +
        sleepQuality * 25 +
        activityLevel * 25 +
        heartRateVariability / 100 * 10 +
        bodyBalance / 10 +
        recoveryIndex / 10);
  }

  /// 判断健康状况
  String getHealthStatus() {
    final score = getOverallScore();

    if (score >= 80) {
      return '优秀';
    } else if (score >= 70) {
      return '良好';
    } else if (score >= 60) {
      return '一般';
    } else {
      return '需要改善';
    }
  }
}
