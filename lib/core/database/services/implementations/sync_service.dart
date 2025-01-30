import 'package:get/get.dart';
import '../models/sync_log.dart';
import '../models/sync_settings.dart';
import 'storage_manager.dart';
import 'connectivity_service.dart';
import 'dart:async';

class SyncService extends GetxService {
  final _storage = Get.find<StorageManager>();
  static const _settingsKey = 'sync_settings';

  final syncProgress = Rx<SyncProgress>(SyncProgress.initial());
  final maxRetries = 3;

  final _syncCanceller = CancelableCompleter();
  final _logController = Get.find<SyncLogController>();

  // 获取同步设置
  Future<SyncSettings> getSettings() async {
    try {
      final json = _storage.getString(_settingsKey);
      if (json != null) {
        return SyncSettings.fromJson(Map<String, dynamic>.from(
          const JsonDecoder().convert(json),
        ));
      }
      return const SyncSettings(
        autoSync: false,
        interval: '每天',
        range: '最近7天',
        conflictStrategy: '手动处理',
      );
    } catch (e) {
      throw Exception('获取同步设置失败: $e');
    }
  }

  // 保存同步设置
  Future<void> saveSettings({
    required bool autoSync,
    required String interval,
    required String range,
    required String conflictStrategy,
  }) async {
    try {
      final settings = SyncSettings(
        autoSync: autoSync,
        interval: interval,
        range: range,
        conflictStrategy: conflictStrategy,
      );
      await _storage.setString(
        _settingsKey,
        const JsonEncoder().convert(settings.toJson()),
      );
    } catch (e) {
      throw Exception('保存设置失败: $e');
    }
  }

  Future<List<SyncLog>> getLogs() async {
    try {
      // TODO: 从API获取同步日志
      // 模拟数据
      return [
        SyncLog(
          id: '1',
          timestamp: DateTime.now(),
          type: '全量同步',
          status: '成功',
          details: '同步完成',
          recordCount: 100,
        ),
        SyncLog(
          id: '2',
          timestamp: DateTime.now().subtract(const Duration(hours: 1)),
          type: '增量同步',
          status: '成功',
          details: '新增数据同步完成',
          recordCount: 10,
        ),
      ];
    } catch (e) {
      throw Exception('获取同步日志失败: $e');
    }
  }

  Future<void> clearLogs() async {
    try {
      // TODO: 调用API清除同步日志
      await Future.delayed(const Duration(seconds: 1));
    } catch (e) {
      throw Exception('清除同步日志失败: $e');
    }
  }

  Future<void> sync() async {
    final connectivityService = Get.find<ConnectivityService>();
    if (!connectivityService.hasConnection) {
      await _logSyncEvent(
        type: '同步失败',
        status: '失败',
        details: '无网络连接',
        recordCount: 0,
      );
      throw Exception('无网络连接');
    }

    int retryCount = 0;
    while (retryCount < maxRetries) {
      try {
        _syncCanceller.complete = Completer();
        await _performSync();
        await _logSyncEvent(
          type: '全量同步',
          status: '成功',
          details: '同步完成',
          recordCount: syncProgress.value.total,
        );
        return;
      } catch (e) {
        retryCount++;
        if (retryCount >= maxRetries) {
          await _logSyncEvent(
            type: '同步失败',
            status: '失败',
            details: '已重试$maxRetries次: $e',
            recordCount: 0,
          );
          throw Exception('同步失败，已重试$maxRetries次: $e');
        }
        await Future.delayed(Duration(seconds: retryCount * 2));
      }
    }
  }

  Future<void> cancelSync() async {
    _syncCanceller.operation.cancel();
    syncProgress.value = syncProgress.value.copyWith(
      stage: '已取消',
      message: '同步已取消',
    );
    await _logSyncEvent(
      type: '同步取消',
      status: '取消',
      details: '用户取消同步',
      recordCount: syncProgress.value.current,
    );
  }

  Future<void> _logSyncEvent({
    required String type,
    required String status,
    required String details,
    required int recordCount,
  }) async {
    final log = SyncLog(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      timestamp: DateTime.now(),
      type: type,
      status: status,
      details: details,
      recordCount: recordCount,
    );
    await _logController.addLog(log);
  }

  Future<void> _performSync() async {
    try {
      // 准备阶段
      syncProgress.value = SyncProgress.initial();
      await Future.delayed(const Duration(seconds: 1));

      // 上传本地数据
      syncProgress.value = syncProgress.value.copyWith(
        stage: '上传数据',
        message: '正在上传本地数据...',
        total: 100,
      );

      for (int i = 0; i < 100; i++) {
        if (_syncCanceller.operation.isCanceled) {
          throw CancelException();
        }
        // 模拟上传进度
        await Future.delayed(const Duration(milliseconds: 50));
        syncProgress.value = syncProgress.value.copyWith(
          current: i + 1,
          percentage: (i + 1) / 100,
          message: '正在上传数据 ${i + 1}/100',
        );
      }

      // 下载云端数据
      syncProgress.value = syncProgress.value.copyWith(
        stage: '下载数据',
        message: '正在下载云端数据...',
        current: 0,
        total: 50,
      );

      for (int i = 0; i < 50; i++) {
        // 模拟下载进度
        await Future.delayed(const Duration(milliseconds: 100));
        syncProgress.value = syncProgress.value.copyWith(
          current: i + 1,
          percentage: (i + 1) / 50,
          message: '正在下载数据 ${i + 1}/50',
        );
      }

      // 完成同步
      syncProgress.value = syncProgress.value.copyWith(
        stage: '完成',
        message: '同步完成',
        percentage: 1.0,
      );
    } on CancelException {
      throw Exception('同步已取消');
    } catch (e) {
      syncProgress.value = syncProgress.value.copyWith(
        stage: '错误',
        message: '同步失败: $e',
      );
      rethrow;
    }
  }
}

class CancelableCompleter {
  Completer<void>? _completer;
  final _operation = CancelableOperation.fromValue(null);

  set complete(Completer<void> completer) {
    _completer = completer;
  }

  CancelableOperation get operation => _operation;
}

class CancelException implements Exception {}
