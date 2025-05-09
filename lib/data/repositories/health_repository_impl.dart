import 'dart:convert';

import 'package:shared_preferences/shared_preferences.dart';
import 'package:suoke_life/domain/models/health_record_model.dart';
import 'package:suoke_life/domain/repositories/health_repository.dart';
import 'package:uuid/uuid.dart';

/// 健康数据仓库实现
///
/// 本实现使用SharedPreferences作为临时存储，实际项目中可替换为SQLite或远程API
class HealthRepositoryImpl implements HealthRepository {
  final SharedPreferences _prefs;
  final _uuid = const Uuid();

  /// 构造函数
  HealthRepositoryImpl(this._prefs);

  /// 获取健康记录存储键
  String _getStorageKey(String userId, HealthDataType? type) {
    return type != null
        ? 'health_records_${userId}_${type.toString()}'
        : 'health_records_$userId';
  }

  /// 保存记录列表到存储
  Future<void> _saveRecordsList(
      List<HealthRecord> records, String userId) async {
    final allRecordsMap = <String, List<String>>{};

    // 按类型分组记录
    for (final record in records) {
      final key = _getStorageKey(userId, record.type);
      if (!allRecordsMap.containsKey(key)) {
        allRecordsMap[key] = [];
      }
      allRecordsMap[key]!.add(jsonEncode(record.toJson()));
    }

    // 保存所有记录
    final allKey = _getStorageKey(userId, null);
    await _prefs.setStringList(
      allKey,
      records.map((r) => jsonEncode(r.toJson())).toList(),
    );

    // 保存按类型分组的记录
    for (final entry in allRecordsMap.entries) {
      await _prefs.setStringList(entry.key, entry.value);
    }
  }

  /// 将JSON转换为健康记录实例
  HealthRecord _recordFromJson(Map<String, dynamic> json) {
    final typeStr = json['type'] as String;
    final type = HealthDataType.values.firstWhere(
      (t) => t.toString() == typeStr,
      orElse: () => HealthDataType.sleep,
    );

    switch (type) {
      case HealthDataType.sleep:
        return SleepRecord.fromJson(json);
      case HealthDataType.bloodPressure:
        return BloodPressureRecord.fromJson(json);
      case HealthDataType.weight:
        return WeightRecord.fromJson(json);
      case HealthDataType.heartRate:
        return HeartRateRecord.fromJson(json);
      default:
        throw UnimplementedError('未实现的健康记录类型: $type');
    }
  }

  @override
  Future<List<HealthRecord>> getAllRecords(String userId) async {
    final key = _getStorageKey(userId, null);
    final jsonStrings = _prefs.getStringList(key) ?? [];

    return jsonStrings
        .map((str) => jsonDecode(str) as Map<String, dynamic>)
        .map(_recordFromJson)
        .toList();
  }

  @override
  Future<List<HealthRecord>> getRecordsByType(
      String userId, HealthDataType type) async {
    final key = _getStorageKey(userId, type);
    final jsonStrings = _prefs.getStringList(key) ?? [];

    return jsonStrings
        .map((str) => jsonDecode(str) as Map<String, dynamic>)
        .map(_recordFromJson)
        .toList();
  }

  @override
  Future<List<HealthRecord>> getRecentRecords(String userId, int limit,
      {HealthDataType? type}) async {
    final records = type != null
        ? await getRecordsByType(userId, type)
        : await getAllRecords(userId);

    // 按记录时间排序
    records.sort((a, b) => b.recordTime.compareTo(a.recordTime));

    // 返回最近的记录
    return records.take(limit).toList();
  }

  @override
  Future<List<HealthRecord>> getRecordsByDateRange(
      String userId, DateTime startDate, DateTime endDate,
      {HealthDataType? type}) async {
    final records = type != null
        ? await getRecordsByType(userId, type)
        : await getAllRecords(userId);

    // 过滤日期范围内的记录
    return records.where((record) {
      final recordDate = record.recordTime;
      return recordDate.isAfter(startDate) &&
          recordDate.isBefore(endDate.add(const Duration(days: 1)));
    }).toList();
  }

  @override
  Future<HealthRecord> addRecord(HealthRecord record) async {
    // 如果是新记录，生成ID
    final healthRecord =
        record.id.isEmpty ? _createRecordWithId(record) : record;

    // 获取现有记录
    final existingRecords = await getAllRecords(healthRecord.userId);

    // 添加新记录
    existingRecords.add(healthRecord);

    // 保存记录
    await _saveRecordsList(existingRecords, healthRecord.userId);

    return healthRecord;
  }

  /// 为记录生成新ID
  HealthRecord _createRecordWithId(HealthRecord record) {
    final newId = _uuid.v4();

    switch (record.type) {
      case HealthDataType.sleep:
        final sleepRecord = record as SleepRecord;
        return SleepRecord(
          id: newId,
          recordTime: record.recordTime,
          userId: record.userId,
          startTime: sleepRecord.startTime,
          endTime: sleepRecord.endTime,
          durationHours: sleepRecord.durationHours,
          quality: sleepRecord.quality,
          hasInterruption: sleepRecord.hasInterruption,
          note: record.note,
        );
      case HealthDataType.bloodPressure:
        final bpRecord = record as BloodPressureRecord;
        return BloodPressureRecord(
          id: newId,
          recordTime: record.recordTime,
          userId: record.userId,
          systolic: bpRecord.systolic,
          diastolic: bpRecord.diastolic,
          pulse: bpRecord.pulse,
          note: record.note,
        );
      case HealthDataType.weight:
        final weightRecord = record as WeightRecord;
        return WeightRecord(
          id: newId,
          recordTime: record.recordTime,
          userId: record.userId,
          weight: weightRecord.weight,
          bmi: weightRecord.bmi,
          bodyFat: weightRecord.bodyFat,
          muscleMass: weightRecord.muscleMass,
          note: record.note,
        );
      case HealthDataType.heartRate:
        final hrRecord = record as HeartRateRecord;
        return HeartRateRecord(
          id: newId,
          recordTime: record.recordTime,
          userId: record.userId,
          beatsPerMinute: hrRecord.beatsPerMinute,
          measurementContext: hrRecord.measurementContext,
          note: record.note,
        );
      default:
        throw UnimplementedError('未实现的健康记录类型: ${record.type}');
    }
  }

  @override
  Future<HealthRecord?> getRecordById(String id) async {
    // 由于没有直接的ID索引，需要搜索所有记录
    // 在实际应用中，应该使用更高效的存储和索引
    final allUsers = await _prefs.getKeys();
    final userIds = allUsers
        .where((key) => key.startsWith('health_records_'))
        .map((key) => key.split('_')[2])
        .toSet();

    for (final userId in userIds) {
      final records = await getAllRecords(userId);
      for (final record in records) {
        if (record.id == id) {
          return record;
        }
      }
    }

    return null;
  }

  @override
  Future<HealthRecord> updateRecord(HealthRecord record) async {
    // 获取所有记录
    final existingRecords = await getAllRecords(record.userId);

    // 查找并更新目标记录
    final recordIndex = existingRecords.indexWhere((r) => r.id == record.id);
    if (recordIndex >= 0) {
      existingRecords[recordIndex] = record;

      // 保存更新后的记录列表
      await _saveRecordsList(existingRecords, record.userId);
      return record;
    } else {
      throw Exception('记录不存在: ${record.id}');
    }
  }

  @override
  Future<bool> deleteRecord(String id) async {
    // 由于没有直接的ID索引，需要搜索所有记录
    final allUsers = await _prefs.getKeys();
    final userIds = allUsers
        .where((key) => key.startsWith('health_records_'))
        .map((key) => key.split('_')[2])
        .toSet();

    for (final userId in userIds) {
      final records = await getAllRecords(userId);
      final initialCount = records.length;

      records.removeWhere((record) => record.id == id);

      if (records.length < initialCount) {
        // 找到并删除了记录
        await _saveRecordsList(records, userId);
        return true;
      }
    }

    return false;
  }

  @override
  Future<HealthRecord?> getLatestRecord(
      String userId, HealthDataType type) async {
    final records = await getRecordsByType(userId, type);

    if (records.isEmpty) {
      return null;
    }

    // 按记录时间排序
    records.sort((a, b) => b.recordTime.compareTo(a.recordTime));

    // 返回最新记录
    return records.first;
  }

  @override
  Future<Map<String, dynamic>> getStatistics(String userId, HealthDataType type,
      DateTime startDate, DateTime endDate) async {
    final records = await getRecordsByDateRange(
      userId,
      startDate,
      endDate,
      type: type,
    );

    if (records.isEmpty) {
      return {'count': 0};
    }

    // 基本统计信息
    final result = <String, dynamic>{
      'count': records.length,
      'startDate': startDate.toIso8601String(),
      'endDate': endDate.toIso8601String(),
    };

    // 根据记录类型计算特定的统计信息
    switch (type) {
      case HealthDataType.sleep:
        final sleepRecords = records.cast<SleepRecord>();
        final durations = sleepRecords.map((r) => r.durationHours).toList();
        result['average'] =
            durations.reduce((a, b) => a + b) / durations.length;
        result['max'] = durations.reduce((a, b) => a > b ? a : b);
        result['min'] = durations.reduce((a, b) => a < b ? a : b);
        break;
      case HealthDataType.bloodPressure:
        final bpRecords = records.cast<BloodPressureRecord>();
        final systolicValues = bpRecords.map((r) => r.systolic).toList();
        final diastolicValues = bpRecords.map((r) => r.diastolic).toList();

        result['averageSystolic'] =
            systolicValues.reduce((a, b) => a + b) / systolicValues.length;
        result['averageDiastolic'] =
            diastolicValues.reduce((a, b) => a + b) / diastolicValues.length;
        result['maxSystolic'] = systolicValues.reduce((a, b) => a > b ? a : b);
        result['minSystolic'] = systolicValues.reduce((a, b) => a < b ? a : b);
        result['maxDiastolic'] =
            diastolicValues.reduce((a, b) => a > b ? a : b);
        result['minDiastolic'] =
            diastolicValues.reduce((a, b) => a < b ? a : b);
        break;
      case HealthDataType.weight:
        final weightRecords = records.cast<WeightRecord>();
        final weights = weightRecords.map((r) => r.weight).toList();

        result['average'] = weights.reduce((a, b) => a + b) / weights.length;
        result['max'] = weights.reduce((a, b) => a > b ? a : b);
        result['min'] = weights.reduce((a, b) => a < b ? a : b);
        break;
      case HealthDataType.heartRate:
        final hrRecords = records.cast<HeartRateRecord>();
        final rates = hrRecords.map((r) => r.beatsPerMinute).toList();

        result['average'] = rates.reduce((a, b) => a + b) / rates.length;
        result['max'] = rates.reduce((a, b) => a > b ? a : b);
        result['min'] = rates.reduce((a, b) => a < b ? a : b);
        break;
      default:
        // 其他记录类型的统计信息可以在此扩展
        break;
    }

    return result;
  }
}
