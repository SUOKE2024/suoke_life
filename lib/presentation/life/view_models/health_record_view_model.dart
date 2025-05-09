import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/domain/models/health_record_model.dart';
import 'package:suoke_life/domain/repositories/health_repository.dart';
import 'package:suoke_life/di/providers.dart';

/// 健康记录状态
class HealthRecordState {
  /// 是否加载中
  final bool isLoading;
  
  /// 错误信息
  final String? errorMessage;
  
  /// 健康记录列表
  final List<HealthRecord> records;

  /// 构造函数
  const HealthRecordState({
    this.isLoading = false,
    this.errorMessage,
    this.records = const [],
  });

  /// 复制方法
  HealthRecordState copyWith({
    bool? isLoading,
    String? errorMessage,
    List<HealthRecord>? records,
  }) {
    return HealthRecordState(
      isLoading: isLoading ?? this.isLoading,
      errorMessage: errorMessage,
      records: records ?? this.records,
    );
  }
}

/// 健康记录视图模型
class HealthRecordViewModel extends StateNotifier<HealthRecordState> {
  /// 健康仓库
  final HealthRepository _healthRepository;
  
  /// 初始状态
  static const initialState = HealthRecordState();

  /// 构造函数
  HealthRecordViewModel(this._healthRepository) : super(initialState);

  /// 获取最近的健康记录
  Future<void> getRecentRecords(int count, {HealthDataType? type}) async {
    state = state.copyWith(isLoading: true, errorMessage: null);

    try {
      final records = await _healthRepository.getRecentRecords('current_user', count, type: type);
      state = state.copyWith(isLoading: false, records: records);
    } catch (e) {
      state = state.copyWith(isLoading: false, errorMessage: e.toString());
    }
  }

  /// 获取用户所有健康记录
  Future<void> getAllRecords() async {
    state = state.copyWith(isLoading: true, errorMessage: null);

    try {
      final records = await _healthRepository.getAllRecords('current_user');
      state = state.copyWith(isLoading: false, records: records);
    } catch (e) {
      state = state.copyWith(isLoading: false, errorMessage: '获取健康记录失败: ${e.toString()}');
    }
  }

  /// 获取用户特定类型的健康记录
  Future<void> getRecordsByType(HealthDataType type) async {
    state = state.copyWith(isLoading: true, errorMessage: null);

    try {
      final records = await _healthRepository.getRecordsByType('current_user', type);
      state = state.copyWith(isLoading: false, records: records);
    } catch (e) {
      state = state.copyWith(isLoading: false, errorMessage: '获取${type.name}记录失败: ${e.toString()}');
    }
  }

  /// 获取特定日期范围内的健康记录
  Future<void> getRecordsByDateRange(DateTime startDate, DateTime endDate,
      {HealthDataType? type}) async {
    state = state.copyWith(isLoading: true, errorMessage: null);

    try {
      final records = await _healthRepository.getRecordsByDateRange(
        'current_user',
        startDate,
        endDate,
        type: type,
      );
      state = state.copyWith(isLoading: false, records: records);
    } catch (e) {
      state = state.copyWith(isLoading: false, errorMessage: '获取日期范围内记录失败: ${e.toString()}');
    }
  }

  /// 添加健康记录
  Future<void> addRecord(HealthRecord record) async {
    state = state.copyWith(isLoading: true, errorMessage: null);

    try {
      final updatedRecord = await _healthRepository.addRecord(record);

      // 更新记录列表
      final updatedRecords = [...state.records, updatedRecord];
      state = state.copyWith(isLoading: false, records: updatedRecords);

      // 更新最新记录
      await _updateLatestRecord(record.type);
    } catch (e) {
      state = state.copyWith(isLoading: false, errorMessage: '添加记录失败: ${e.toString()}');
    }
  }

  /// 更新健康记录
  Future<void> updateRecord(HealthRecord record) async {
    state = state.copyWith(isLoading: true, errorMessage: null);

    try {
      final updatedRecord = await _healthRepository.updateRecord(record);

      // 更新记录列表
      final recordIndex = state.records.indexWhere((r) => r.id == record.id);
      if (recordIndex >= 0) {
        final updatedRecords = [...state.records];
        updatedRecords[recordIndex] = updatedRecord;
        state = state.copyWith(isLoading: false, records: updatedRecords);
      }

      // 更新最新记录
      await _updateLatestRecord(record.type);
    } catch (e) {
      state = state.copyWith(isLoading: false, errorMessage: '更新记录失败: ${e.toString()}');
    }
  }

  /// 删除健康记录
  Future<void> deleteRecord(String id) async {
    state = state.copyWith(isLoading: true, errorMessage: null);

    try {
      // 记录记录类型，以便更新最新记录
      HealthDataType? recordType;
      final record = state.records.firstWhere((r) => r.id == id);
      recordType = record.type;

      final success = await _healthRepository.deleteRecord(id);

      if (success) {
        // 更新记录列表
        final updatedRecords = state.records.where((r) => r.id != id).toList();
        state = state.copyWith(isLoading: false, records: updatedRecords);

        // 更新最新记录
        if (recordType != null) {
          await _updateLatestRecord(recordType);
        }
      } else {
        state = state.copyWith(isLoading: false, errorMessage: '删除记录失败：记录不存在');
      }
    } catch (e) {
      state = state.copyWith(isLoading: false, errorMessage: '删除记录失败: ${e.toString()}');
    }
  }

  /// 获取最新的记录
  Future<void> getLatestRecord(HealthDataType type) async {
    try {
      final record = await _healthRepository.getLatestRecord('current_user', type);
      if (record != null) {
        state = state.copyWith(isLoading: false, records: [...state.records, record]);
      }
    } catch (e) {
      state = state.copyWith(isLoading: false, errorMessage: '获取最新${type.name}记录失败: ${e.toString()}');
    }
  }

  /// 获取健康数据统计信息
  Future<void> getStatistics(
      HealthDataType type, DateTime startDate, DateTime endDate) async {
    try {
      final stats = await _healthRepository.getStatistics(
        'current_user',
        type,
        startDate,
        endDate,
      );
      state = state.copyWith(isLoading: false, records: state.records, errorMessage: null);
    } catch (e) {
      state = state.copyWith(isLoading: false, errorMessage: '获取${type.name}统计信息失败: ${e.toString()}');
    }
  }

  /// 更新最新记录的辅助方法
  Future<void> _updateLatestRecord(HealthDataType type) async {
    await getLatestRecord(type);
  }

  /// 加载健康数据概览
  Future<void> loadHealthDataOverview() async {
    // 加载最近的记录
    await getRecentRecords(10);

    // 加载各类型的最新记录
    await getLatestRecord(HealthDataType.sleep);
    await getLatestRecord(HealthDataType.bloodPressure);
    await getLatestRecord(HealthDataType.weight);
    await getLatestRecord(HealthDataType.heartRate);

    // 加载7天的统计数据
    final now = DateTime.now();
    final weekAgo = now.subtract(const Duration(days: 7));

    await getStatistics(HealthDataType.sleep, weekAgo, now);
    await getStatistics(HealthDataType.bloodPressure, weekAgo, now);
    await getStatistics(HealthDataType.weight, weekAgo, now);
    await getStatistics(HealthDataType.heartRate, weekAgo, now);
  }

  /// 根据ID获取单条健康记录
  Future<HealthRecord?> getRecordById(String id) async {
    state = state.copyWith(isLoading: true, errorMessage: null);

    try {
      final record = await _healthRepository.getRecordById(id);

      if (record != null) {
        // 如果记录不在当前记录列表中，将其添加到列表
        final existingIndex = state.records.indexWhere((r) => r.id == id);
        if (existingIndex < 0) {
          final updatedRecords = [...state.records, record];
          state = state.copyWith(isLoading: false, records: updatedRecords);
        }
      }

      return record;
    } catch (e) {
      state = state.copyWith(isLoading: false, errorMessage: '获取健康记录失败: ${e.toString()}');
      return null;
    }
  }
}
