import 'package:equatable/equatable.dart';
import 'package:uuid/uuid.dart';

/// 健康数据类型枚举
enum HealthDataType {
  /// 睡眠记录
  sleep,
  
  /// 血压记录
  bloodPressure,
  
  /// 体重记录
  weight,
  
  /// 心率记录
  heartRate,
  
  /// 血糖记录
  bloodGlucose,
}

/// 健康数据类型扩展
extension HealthDataTypeExtension on HealthDataType {
  /// 获取健康数据类型名称
  String get name {
    switch (this) {
      case HealthDataType.sleep:
        return '睡眠';
      case HealthDataType.bloodPressure:
        return '血压';
      case HealthDataType.weight:
        return '体重';
      case HealthDataType.heartRate:
        return '心率';
      case HealthDataType.bloodGlucose:
        return '血糖';
    }
  }

  /// 获取健康数据单位
  String get unit {
    switch (this) {
      case HealthDataType.sleep:
        return '小时';
      case HealthDataType.bloodPressure:
        return 'mmHg';
      case HealthDataType.weight:
        return 'kg';
      case HealthDataType.heartRate:
        return '次/分';
      case HealthDataType.bloodGlucose:
        return 'mmol/L';
    }
  }
}

/// 健康记录基类
abstract class HealthRecord extends Equatable {
  /// 记录ID
  final String id;
  
  /// 用户ID
  final String userId;
  
  /// 记录时间
  final DateTime recordTime;
  
  /// 记录类型
  final HealthDataType type;
  
  /// 记录备注
  final String? note;

  /// 构造函数
  const HealthRecord({
    required this.id,
    required this.userId,
    required this.recordTime,
    required this.type,
    this.note,
  });

  /// 转换为JSON
  Map<String, dynamic> toJson();

  @override
  List<Object?> get props => [id, recordTime, type, note, userId];
}

/// 睡眠记录
class SleepRecord extends HealthRecord {
  /// 入睡时间
  final DateTime startTime;
  
  /// 起床时间
  final DateTime endTime;
  
  /// 睡眠时长(小时)
  final double durationHours;
  
  /// 睡眠质量评分(1-5)
  final double? quality;
  
  /// 是否有中断
  final bool hasInterruption;
  
  /// 是否有梦境
  final bool hadDreams;
  
  /// 环境
  final String? environment;

  /// 构造函数
  const SleepRecord({
    required String id,
    required String userId,
    required DateTime recordTime,
    String? note,
    required this.startTime,
    required this.endTime,
    required this.durationHours,
    this.quality,
    this.hasInterruption = false,
    this.hadDreams = false,
    this.environment,
  }) : super(
          id: id,
          userId: userId,
          recordTime: recordTime,
          type: HealthDataType.sleep,
          note: note,
        );

  /// 创建示例数据
  factory SleepRecord.sample() {
    final uuid = const Uuid().v4();
    final now = DateTime.now();
    final yesterday = now.subtract(const Duration(days: 1));
    
    // 生成昨天晚上10点到今天早上6点的睡眠记录
    final startTime = DateTime(yesterday.year, yesterday.month, yesterday.day, 22, 30);
    final endTime = DateTime(now.year, now.month, now.day, 6, 30);
    final durationHours = endTime.difference(startTime).inMinutes / 60;
    
    return SleepRecord(
      id: uuid,
      userId: 'current_user',
      recordTime: now,
      startTime: startTime,
      endTime: endTime,
      durationHours: durationHours,
      quality: 4.0, // 0-5分
      hadDreams: true,
      environment: '家里',
      note: '昨晚睡得还不错，但凌晨醒了一次',
    );
  }

  factory SleepRecord.fromJson(Map<String, dynamic> json) {
    return SleepRecord(
      id: json['id'],
      recordTime: DateTime.parse(json['record_time']),
      userId: json['user_id'],
      startTime: DateTime.parse(json['start_time']),
      endTime: DateTime.parse(json['end_time']),
      durationHours: json['duration_hours'],
      quality: json['quality'],
      hasInterruption: json['has_interruption'] ?? false,
      hadDreams: json['had_dreams'] ?? false,
      environment: json['environment'],
      note: json['note'],
    );
  }

  @override
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'record_time': recordTime.toIso8601String(),
      'user_id': userId,
      'type': type.toString(),
      'start_time': startTime.toIso8601String(),
      'end_time': endTime.toIso8601String(),
      'duration_hours': durationHours,
      'quality': quality,
      'has_interruption': hasInterruption,
      'had_dreams': hadDreams,
      'environment': environment,
      'note': note,
    };
  }

  @override
  List<Object?> get props => [
        id,
        userId,
        recordTime,
        type,
        note,
        startTime,
        endTime,
        durationHours,
        quality,
        hasInterruption,
        hadDreams,
        environment,
      ];
}

/// 血压记录
class BloodPressureRecord extends HealthRecord {
  /// 收缩压(mmHg)
  final int systolic;
  
  /// 舒张压(mmHg)
  final int diastolic;
  
  /// 脉搏(bpm)
  final int? pulse;

  /// 构造函数
  const BloodPressureRecord({
    required String id,
    required String userId,
    required DateTime recordTime,
    required this.systolic,
    required this.diastolic,
    this.pulse,
    String? note,
  }) : super(
          id: id,
          userId: userId,
          recordTime: recordTime,
          type: HealthDataType.bloodPressure,
          note: note,
        );

  factory BloodPressureRecord.fromJson(Map<String, dynamic> json) {
    return BloodPressureRecord(
      id: json['id'],
      recordTime: DateTime.parse(json['record_time']),
      userId: json['user_id'],
      systolic: json['systolic'],
      diastolic: json['diastolic'],
      pulse: json['pulse'],
      note: json['note'],
    );
  }

  @override
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'record_time': recordTime.toIso8601String(),
      'user_id': userId,
      'type': type.toString(),
      'systolic': systolic,
      'diastolic': diastolic,
      'pulse': pulse,
      'note': note,
    };
  }

  @override
  List<Object?> get props => [
        id,
        userId,
        recordTime,
        type,
        note,
        systolic,
        diastolic,
        pulse,
      ];
}

/// 体重记录
class WeightRecord extends HealthRecord {
  /// 体重(kg)
  final double weight;
  
  /// BMI
  final double? bmi;
  
  /// 体脂率(%)
  final double? bodyFat;
  
  /// 肌肉量(kg)
  final double? muscleMass;

  /// 构造函数
  const WeightRecord({
    required String id,
    required String userId,
    required DateTime recordTime,
    required this.weight,
    this.bmi,
    this.bodyFat,
    this.muscleMass,
    String? note,
  }) : super(
          id: id,
          userId: userId,
          recordTime: recordTime,
          type: HealthDataType.weight,
          note: note,
        );

  factory WeightRecord.fromJson(Map<String, dynamic> json) {
    return WeightRecord(
      id: json['id'],
      recordTime: DateTime.parse(json['record_time']),
      userId: json['user_id'],
      weight: json['weight'],
      bmi: json['bmi'],
      bodyFat: json['body_fat'],
      muscleMass: json['muscle_mass'],
      note: json['note'],
    );
  }

  @override
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'record_time': recordTime.toIso8601String(),
      'user_id': userId,
      'type': type.toString(),
      'weight': weight,
      'bmi': bmi,
      'body_fat': bodyFat,
      'muscle_mass': muscleMass,
      'note': note,
    };
  }

  @override
  List<Object?> get props => [
        id,
        userId,
        recordTime,
        type,
        note,
        weight,
        bmi,
        bodyFat,
        muscleMass,
      ];
}

/// 心率记录
class HeartRateRecord extends HealthRecord {
  /// 心率(bpm)
  final int beatsPerMinute;
  
  /// 测量场景
  final String? measurementContext;

  /// 构造函数
  const HeartRateRecord({
    required String id,
    required String userId,
    required DateTime recordTime,
    required this.beatsPerMinute,
    this.measurementContext,
    String? note,
  }) : super(
          id: id,
          userId: userId,
          recordTime: recordTime,
          type: HealthDataType.heartRate,
          note: note,
        );

  factory HeartRateRecord.fromJson(Map<String, dynamic> json) {
    return HeartRateRecord(
      id: json['id'],
      recordTime: DateTime.parse(json['record_time']),
      userId: json['user_id'],
      beatsPerMinute: json['beats_per_minute'],
      measurementContext: json['measurement_context'],
      note: json['note'],
    );
  }

  @override
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'record_time': recordTime.toIso8601String(),
      'user_id': userId,
      'type': type.toString(),
      'beats_per_minute': beatsPerMinute,
      'measurement_context': measurementContext,
      'note': note,
    };
  }

  @override
  List<Object?> get props => [
        id,
        userId,
        recordTime,
        type,
        note,
        beatsPerMinute,
        measurementContext,
      ];
}

/// 血糖记录
class BloodGlucoseRecord extends HealthRecord {
  /// 血糖值(mmol/L)
  final double value;
  
  /// 测量时段
  final GlucoseMeasurementPeriod period;
  
  /// 是否空腹
  final bool isFasting;

  /// 构造函数
  const BloodGlucoseRecord({
    required String id,
    required String userId,
    required DateTime recordTime,
    String? note,
    required this.value,
    required this.period,
    required this.isFasting,
  }) : super(
          id: id,
          userId: userId,
          recordTime: recordTime,
          type: HealthDataType.bloodGlucose,
          note: note,
        );

  factory BloodGlucoseRecord.fromJson(Map<String, dynamic> json) {
    return BloodGlucoseRecord(
      id: json['id'],
      userId: json['user_id'],
      recordTime: DateTime.parse(json['record_time']),
      value: json['value'],
      period: GlucoseMeasurementPeriod.values.firstWhere(
        (e) => e.toString() == json['period'],
        orElse: () => GlucoseMeasurementPeriod.beforeBreakfast,
      ),
      isFasting: json['is_fasting'] ?? false,
      note: json['note'],
    );
  }

  @override
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'record_time': recordTime.toIso8601String(),
      'type': type.toString(),
      'value': value,
      'period': period.toString(),
      'is_fasting': isFasting,
      'note': note,
    };
  }

  @override
  List<Object?> get props => [id, userId, recordTime, type, note, value, period, isFasting];
}

/// 血糖测量时段枚举
enum GlucoseMeasurementPeriod {
  /// 早餐前
  beforeBreakfast,
  
  /// 早餐后
  afterBreakfast,
  
  /// 午餐前
  beforeLunch,
  
  /// 午餐后
  afterLunch,
  
  /// 晚餐前
  beforeDinner,
  
  /// 晚餐后
  afterDinner,
  
  /// 睡前
  beforeSleep,
  
  /// 凌晨
  dawn,
}

/// 血糖测量时段扩展
extension GlucoseMeasurementPeriodExtension on GlucoseMeasurementPeriod {
  /// 获取时段友好名称
  String get name {
    switch (this) {
      case GlucoseMeasurementPeriod.beforeBreakfast:
        return '早餐前';
      case GlucoseMeasurementPeriod.afterBreakfast:
        return '早餐后';
      case GlucoseMeasurementPeriod.beforeLunch:
        return '午餐前';
      case GlucoseMeasurementPeriod.afterLunch:
        return '午餐后';
      case GlucoseMeasurementPeriod.beforeDinner:
        return '晚餐前';
      case GlucoseMeasurementPeriod.afterDinner:
        return '晚餐后';
      case GlucoseMeasurementPeriod.beforeSleep:
        return '睡前';
      case GlucoseMeasurementPeriod.dawn:
        return '凌晨';
    }
  }
}
