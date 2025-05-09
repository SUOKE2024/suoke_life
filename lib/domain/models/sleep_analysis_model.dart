import 'package:equatable/equatable.dart';
import 'package:suoke_life/domain/models/health_record_model.dart';
import 'dart:math';

/// 睡眠分析模型
class SleepAnalysis extends Equatable {
  /// 分析ID
  final String id;
  
  /// 用户ID
  final String userId;
  
  /// 睡眠记录ID
  final String? recordId;
  
  /// 分析日期
  final DateTime date;
  
  /// 睡眠时长（小时）
  final double durationHours;
  
  /// 深睡时长（小时）
  final double deepSleepHours;
  
  /// 入睡时间
  final DateTime bedtime;
  
  /// 起床时间
  final DateTime wakeTime;
  
  /// 总体睡眠得分（0-100）
  final double overallScore;
  
  /// 中断次数
  final int interruptionCount;
  
  /// 呼吸质量得分（0-100）
  final double? breathingScore;
  
  /// 分析备注
  final String? note;
  
  /// 分析结果
  final SleepAnalysisResult? result;
  
  /// 改善建议
  final List<String> suggestions;
  
  /// 中医体质评估
  final String? tcmEvaluation;
  
  /// 创建时间
  final DateTime createdAt;

  /// 构造函数
  const SleepAnalysis({
    required this.id,
    required this.userId,
    this.recordId,
    required this.date,
    required this.durationHours,
    required this.deepSleepHours,
    required this.bedtime,
    required this.wakeTime,
    required this.overallScore,
    required this.interruptionCount,
    this.breathingScore,
    this.note,
    this.result,
    this.suggestions = const [],
    this.tcmEvaluation,
    required this.createdAt,
  });

  @override
  List<Object?> get props => [
        id,
        userId,
        recordId,
        date,
        durationHours,
        deepSleepHours,
        bedtime,
        wakeTime,
        overallScore,
        interruptionCount,
        breathingScore,
        note,
        result,
        suggestions,
        tcmEvaluation,
        createdAt,
      ];

  /// 从分析结果创建睡眠分析
  factory SleepAnalysis.fromResult(String id, SleepAnalysisResult result) {
    final record = result.sleepRecord;

    // 计算各睡眠阶段时长
    double deepSleepHours = 0;
    double lightSleepHours = 0;
    double remSleepHours = 0;
    double awakeHours = 0;

    for (final stage in result.sleepStages) {
      final hours = stage.durationMinutes / 60.0;
      switch (stage.type) {
        case SleepStageType.deep:
          deepSleepHours += hours;
          break;
        case SleepStageType.light:
          lightSleepHours += hours;
          break;
        case SleepStageType.rem:
          remSleepHours += hours;
          break;
        case SleepStageType.awake:
          awakeHours += hours;
          break;
      }
    }

    return SleepAnalysis(
      id: id,
      userId: '', // Assuming userId is not provided in the result
      recordId: null, // Assuming recordId is not provided in the result
      date: record.recordTime
          .subtract(const Duration(hours: 6)), // 假设凌晨6点前的睡眠算作前一天
      durationHours: record.durationHours,
      deepSleepHours: deepSleepHours,
      bedtime: record.startTime,
      wakeTime: record.endTime,
      overallScore: result.overallScore,
      interruptionCount: result.interruptionCount,
      breathingScore: result.breathingScore,
      note: result.note,
      result: result,
      suggestions: result.improvementSuggestions,
      tcmEvaluation: result.tcmEvaluation,
      createdAt: DateTime.now(),
    );
  }

  /// 创建示例睡眠分析数据
  factory SleepAnalysis.sample({
    required String id,
    required DateTime date,
  }) {
    final random = Random();

    // 生成随机的睡眠开始和结束时间
    final bedtime = DateTime(
        date.year,
        date.month,
        date.day,
        21 + random.nextInt(3), // 晚上9点到11点入睡
        random.nextInt(60));

    // 随机生成6-9小时的睡眠时间
    final durationHours = 6 + random.nextInt(3) + random.nextDouble();

    // 计算起床时间
    final wakeTime = bedtime.add(Duration(
        hours: durationHours.floor(),
        minutes: ((durationHours - durationHours.floor()) * 60).round()));

    // 生成随机的睡眠周期数据
    final deepSleepHours =
        durationHours * (0.15 + random.nextDouble() * 0.1); // 深度睡眠占15-25%
    final remSleepHours =
        durationHours * (0.2 + random.nextDouble() * 0.1); // REM睡眠占20-30%
    final lightSleepHours =
        durationHours * (0.45 + random.nextDouble() * 0.1); // 轻度睡眠占45-55%
    final awakeHours = durationHours -
        deepSleepHours -
        remSleepHours -
        lightSleepHours; // 醒着的时间

    // 生成其他随机数据
    final timeToFallAsleepMinutes = random.nextInt(30);
    final overallScore = 70.0 + random.nextInt(30); // 70-100分
    final efficiency = 80.0 + random.nextInt(15); // 80-95%
    final interruptionCount = random.nextInt(3);

    return SleepAnalysis(
      id: id,
      userId: '', // Assuming userId is not provided in the sample
      recordId: null, // Assuming recordId is not provided in the sample
      date: date,
      durationHours: durationHours,
      deepSleepHours: deepSleepHours,
      bedtime: bedtime,
      wakeTime: wakeTime,
      overallScore: overallScore,
      interruptionCount: interruptionCount,
      breathingScore: null,
      note: null,
      result: null,
      suggestions: [],
      tcmEvaluation: null,
      createdAt: DateTime.now(),
    );
  }

  /// 根据分数获取睡眠质量等级
  static SleepQualityLevel _getQualityLevelFromScore(double score) {
    if (score >= 90) return SleepQualityLevel.excellent;
    if (score >= 80) return SleepQualityLevel.good;
    if (score >= 70) return SleepQualityLevel.average;
    if (score >= 60) return SleepQualityLevel.poor;
    return SleepQualityLevel.veryPoor;
  }

  /// 生成随机中医体质影响
  static Map<String, double> _generateRandomBodyConstitutionEffects() {
    final random = Random();
    return {
      '气虚质': -0.5 + random.nextDouble(),
      '阳虚质': -0.2 + random.nextDouble() * 0.4,
      '阴虚质': -0.3 + random.nextDouble() * 0.6,
      '痰湿质': -0.4 + random.nextDouble() * 0.8,
      '湿热质': -0.2 + random.nextDouble() * 0.4,
      '血瘀质': -0.3 + random.nextDouble() * 0.6,
      '气郁质': -0.5 + random.nextDouble(),
      '特禀质': -0.1 + random.nextDouble() * 0.2,
      '平和质': random.nextDouble() * 0.5,
    };
  }

  /// 生成随机中医改善建议
  static List<String> _generateRandomTCMRecommendations() {
    final allRecommendations = [
      '百会穴按摩：睡前用拇指指腹按揉百会穴（头顶正中）1-3分钟，有助安神定志。',
      '足三里穴按摩：每天按摩足三里穴（膝盖下四横指，胫骨外侧一横指），增强脾胃功能。',
      '神门穴按摩：睡前按摩手腕内侧的神门穴，有助于镇静安神。',
      '合谷穴按摩：拇指和食指之间的合谷穴，按摩可调和气血，改善睡眠。',
      '睡前温水泡脚：睡前用40℃左右的温水泡脚20分钟，可温通经络，改善睡眠。',
      '睡前喝杯温牛奶：牛奶中含有色氨酸，能促进褪黑素分泌，有助入睡。',
      '助眠茶饮：可选用酸枣仁、远志、合欢花等中药泡水饮用，有助安神助眠。',
      '睡前避免使用电子产品：蓝光会抑制褪黑素分泌，建议睡前1小时避开电子产品。',
      '保持规律作息：尽量固定睡眠和起床时间，有助于调整生物钟。',
      '睡前轻度拉伸：简单的全身拉伸运动可以放松肌肉，促进入睡。',
      '睡前听舒缓音乐：有助于放松心情，减轻压力，促进入睡。',
      '穴位贴敷：可在睡前贴敷神门、足三里等穴位，改善睡眠质量。',
      '艾灸调理：适当的艾灸可温经通络，调和气血，改善睡眠。',
      '睡前避免进食：睡前2小时避免进食，尤其是油腻、刺激性食物。',
      '睡眠环境：保持安静、黑暗、通风良好的睡眠环境。',
    ];

    final random = Random();
    final count = 3 + random.nextInt(3); // 随机选择3-5条建议
    final selected = <String>[];

    while (selected.length < count) {
      final recommendation =
          allRecommendations[random.nextInt(allRecommendations.length)];
      if (!selected.contains(recommendation)) {
        selected.add(recommendation);
      }
    }

    return selected;
  }

  /// 生成随机睡眠阶段
  static List<SleepStage> _generateRandomSleepStages() {
    final random = Random();
    final stages = <SleepStage>[];

    // 生成当前日期
    final date = DateTime.now();

    // 睡眠开始时间
    final bedtime = DateTime(
        date.year,
        date.month,
        date.day,
        22, // 晚上10点入睡
        random.nextInt(60));

    // 当前时间从睡眠开始算起
    var currentTime = bedtime;

    // 入睡阶段 - 清醒
    var stageEnd = currentTime.add(Duration(minutes: 10 + random.nextInt(20)));
    stages.add(SleepStage(
      type: SleepStageType.awake,
      startTime: currentTime,
      endTime: stageEnd,
      durationMinutes: stageEnd.difference(currentTime).inMinutes,
    ));
    currentTime = stageEnd;

    // 生成4-5个睡眠周期，每个周期包含轻睡-深睡-REM
    for (int i = 0; i < 4 + random.nextInt(2); i++) {
      // 轻度睡眠
      stageEnd = currentTime.add(Duration(minutes: 30 + random.nextInt(30)));
      stages.add(SleepStage(
        type: SleepStageType.light,
        startTime: currentTime,
        endTime: stageEnd,
        durationMinutes: stageEnd.difference(currentTime).inMinutes,
      ));
      currentTime = stageEnd;

      // 深度睡眠
      stageEnd = currentTime.add(Duration(minutes: 20 + random.nextInt(30)));
      stages.add(SleepStage(
        type: SleepStageType.deep,
        startTime: currentTime,
        endTime: stageEnd,
        durationMinutes: stageEnd.difference(currentTime).inMinutes,
      ));
      currentTime = stageEnd;

      // REM睡眠
      stageEnd = currentTime.add(Duration(minutes: 15 + random.nextInt(30)));
      stages.add(SleepStage(
        type: SleepStageType.rem,
        startTime: currentTime,
        endTime: stageEnd,
        durationMinutes: stageEnd.difference(currentTime).inMinutes,
      ));
      currentTime = stageEnd;

      // 有10%的几率插入短暂清醒
      if (random.nextDouble() < 0.1) {
        stageEnd = currentTime.add(Duration(minutes: 5 + random.nextInt(10)));
        stages.add(SleepStage(
          type: SleepStageType.awake,
          startTime: currentTime,
          endTime: stageEnd,
          durationMinutes: stageEnd.difference(currentTime).inMinutes,
        ));
        currentTime = stageEnd;
      }
    }

    // 最后添加一个清醒阶段
    stageEnd = currentTime.add(Duration(minutes: 5 + random.nextInt(15)));
    stages.add(SleepStage(
      type: SleepStageType.awake,
      startTime: currentTime,
      endTime: stageEnd,
      durationMinutes: stageEnd.difference(currentTime).inMinutes,
    ));

    return stages;
  }
}

/// 睡眠质量等级
enum SleepQualityLevel {
  excellent(4, '优秀'), // 90-100分
  good(3, '良好'), // 75-89分
  average(2, '一般'), // 60-74分
  poor(1, '较差'), // 40-59分
  veryPoor(0, '很差'); // 0-39分

  final int value;
  final String label;

  const SleepQualityLevel(this.value, this.label);

  /// 根据睡眠得分获取质量等级
  static SleepQualityLevel fromScore(double score) {
    if (score >= 90) return excellent;
    if (score >= 75) return good;
    if (score >= 60) return average;
    if (score >= 40) return poor;
    return veryPoor;
  }
}

/// 睡眠阶段类型
enum SleepStageType {
  awake('清醒'),
  light('浅睡眠'),
  deep('深睡眠'),
  rem('快速眼动');

  final String label;

  const SleepStageType(this.label);
}

/// 睡眠阶段
class SleepStage extends Equatable {
  final SleepStageType type;
  final DateTime startTime;
  final DateTime endTime;
  final int durationMinutes;

  const SleepStage({
    required this.type,
    required this.startTime,
    required this.endTime,
    required this.durationMinutes,
  });

  @override
  List<Object?> get props => [type, startTime, endTime, durationMinutes];
}

/// 睡眠分析结果
class SleepAnalysisResult extends Equatable {
  /// 分析的睡眠记录
  final SleepRecord sleepRecord;

  /// 总体睡眠质量得分（0-100）
  final double overallScore;

  /// 睡眠质量等级
  final SleepQualityLevel qualityLevel;

  /// 睡眠效率（有效睡眠时间/床上总时间 * 100%）
  final double efficiency;

  /// 深睡眠比例
  final double deepSleepPercentage;

  /// 浅睡眠比例
  final double lightSleepPercentage;

  /// 快速眼动睡眠比例
  final double remSleepPercentage;

  /// 清醒时间比例
  final double awakePercentage;

  /// 入睡时长（分钟）
  final int timeToFallAsleepMinutes;

  /// 睡眠阶段分布
  final List<SleepStage> sleepStages;

  /// 睡眠中断次数
  final int interruptionCount;

  /// 与中医体质关联的睡眠评估
  final String tcmEvaluation;

  /// 改善建议
  final List<String> improvementSuggestions;

  /// 呼吸质量得分（0-100）
  final double? breathingScore;

  /// 分析备注
  final String? note;

  const SleepAnalysisResult({
    required this.sleepRecord,
    required this.overallScore,
    required this.qualityLevel,
    required this.efficiency,
    required this.deepSleepPercentage,
    required this.lightSleepPercentage,
    required this.remSleepPercentage,
    required this.awakePercentage,
    required this.timeToFallAsleepMinutes,
    required this.sleepStages,
    required this.interruptionCount,
    required this.tcmEvaluation,
    required this.improvementSuggestions,
    this.breathingScore,
    this.note,
  });

  @override
  List<Object?> get props => [
        sleepRecord,
        overallScore,
        qualityLevel,
        efficiency,
        deepSleepPercentage,
        lightSleepPercentage,
        remSleepPercentage,
        awakePercentage,
        timeToFallAsleepMinutes,
        sleepStages,
        interruptionCount,
        tcmEvaluation,
        improvementSuggestions,
        breathingScore,
        note,
      ];

  /// 创建示例数据（用于开发测试）
  factory SleepAnalysisResult.sample(SleepRecord record) {
    final startTime = record.startTime;
    // 生成睡眠阶段
    final stages = <SleepStage>[];
    var currentTime = startTime;

    // 入睡阶段 - 清醒
    var awakeEnd = currentTime.add(const Duration(minutes: 15));
    stages.add(SleepStage(
      type: SleepStageType.awake,
      startTime: currentTime,
      endTime: awakeEnd,
      durationMinutes: 15,
    ));
    currentTime = awakeEnd;

    // 浅睡阶段1
    var lightEnd1 = currentTime.add(const Duration(minutes: 45));
    stages.add(SleepStage(
      type: SleepStageType.light,
      startTime: currentTime,
      endTime: lightEnd1,
      durationMinutes: 45,
    ));
    currentTime = lightEnd1;

    // 深睡阶段1
    var deepEnd1 = currentTime.add(const Duration(minutes: 90));
    stages.add(SleepStage(
      type: SleepStageType.deep,
      startTime: currentTime,
      endTime: deepEnd1,
      durationMinutes: 90,
    ));
    currentTime = deepEnd1;

    // REM阶段1
    var remEnd1 = currentTime.add(const Duration(minutes: 60));
    stages.add(SleepStage(
      type: SleepStageType.rem,
      startTime: currentTime,
      endTime: remEnd1,
      durationMinutes: 60,
    ));
    currentTime = remEnd1;

    // 浅睡阶段2
    var lightEnd2 = currentTime.add(const Duration(minutes: 60));
    stages.add(SleepStage(
      type: SleepStageType.light,
      startTime: currentTime,
      endTime: lightEnd2,
      durationMinutes: 60,
    ));
    currentTime = lightEnd2;

    // 深睡阶段2
    var deepEnd2 = currentTime.add(const Duration(minutes: 60));
    stages.add(SleepStage(
      type: SleepStageType.deep,
      startTime: currentTime,
      endTime: deepEnd2,
      durationMinutes: 60,
    ));
    currentTime = deepEnd2;

    // REM阶段2
    var remEnd2 = currentTime.add(const Duration(minutes: 60));
    stages.add(SleepStage(
      type: SleepStageType.rem,
      startTime: currentTime,
      endTime: remEnd2,
      durationMinutes: 60,
    ));
    currentTime = remEnd2;

    // 清醒阶段2
    var awakeEnd2 = currentTime.add(const Duration(minutes: 10));
    stages.add(SleepStage(
      type: SleepStageType.awake,
      startTime: currentTime,
      endTime: awakeEnd2,
      durationMinutes: 10,
    ));

    // 计算各种睡眠阶段百分比
    int totalMinutes = 0;
    int deepMinutes = 0;
    int lightMinutes = 0;
    int remMinutes = 0;
    int awakeMinutes = 0;

    for (final stage in stages) {
      totalMinutes += stage.durationMinutes;
      switch (stage.type) {
        case SleepStageType.deep:
          deepMinutes += stage.durationMinutes;
          break;
        case SleepStageType.light:
          lightMinutes += stage.durationMinutes;
          break;
        case SleepStageType.rem:
          remMinutes += stage.durationMinutes;
          break;
        case SleepStageType.awake:
          awakeMinutes += stage.durationMinutes;
          break;
      }
    }

    return SleepAnalysisResult(
      sleepRecord: record,
      overallScore: 82.5,
      qualityLevel: SleepQualityLevel.good,
      efficiency: 93.5,
      deepSleepPercentage: deepMinutes / totalMinutes * 100,
      lightSleepPercentage: lightMinutes / totalMinutes * 100,
      remSleepPercentage: remMinutes / totalMinutes * 100,
      awakePercentage: awakeMinutes / totalMinutes * 100,
      timeToFallAsleepMinutes: 15,
      sleepStages: stages,
      interruptionCount: 1,
      tcmEvaluation: '您的睡眠结构基本良好，但有轻微心肝火旺导致的入睡困难和少量睡眠中断，属于心脾两虚型睡眠模式。',
      improvementSuggestions: [
        '晚上10-11点之前入睡，利于养护肝胆',
        '睡前1小时避免使用电子产品，减少蓝光刺激',
        '睡前可饮用1杯温热牛奶或蜂蜜水，有助于安神',
        '可尝试睡前足浴，按摩涌泉穴，帮助改善睡眠质量',
      ],
      breathingScore: null,
      note: null,
    );
  }
}
