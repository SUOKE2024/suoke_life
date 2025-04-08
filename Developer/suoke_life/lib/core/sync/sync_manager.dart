import 'dart:async';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/core/constants/api_constants.dart';
import 'package:suoke_life/core/network/mcp_service.dart';
import 'package:suoke_life/core/storage/preferences_manager.dart';
import 'package:suoke_life/domain/repositories/mcp_repository.dart';
import 'package:suoke_life/core/database/app_database.dart';
import 'package:suoke_life/core/network/api_client.dart';

/// 同步状态枚举
enum SyncStatus {
  /// 空闲状态
  idle,
  
  /// 同步中
  syncing,
  
  /// 同步成功
  succeeded,
  
  /// 同步失败
  failed,
  
  /// 无网络连接
  noConnection,
}

/// 同步类型枚举
enum SyncType {
  /// 用户健康数据
  healthData,
  
  /// 诊断结果
  diagnosticResult,
  
  /// 知识数据
  knowledgeData,
  
  /// 配置数据
  configData,
  
  /// 全部数据
  all,
}

/// 同步管理器
///
/// 负责管理本地数据与远程服务器的同步
class SyncManager {
  /// API客户端
  final ApiClient _apiClient;
  
  /// 数据库
  final AppDatabase _database;
  
  /// 同步状态
  bool _isSyncing = false;
  
  /// 最后同步时间
  DateTime? _lastSyncTime;
  
  /// 同步定时器
  Timer? _syncTimer;
  
  /// 同步间隔（默认6小时）
  Duration _syncInterval = const Duration(hours: 6);
  
  /// 同步状态监听器
  final _syncStatusController = StreamController<SyncStatus>.broadcast();
  
  /// 创建同步管理器
  SyncManager(this._apiClient, this._database);
  
  /// 同步状态流
  Stream<SyncStatus> get syncStatusStream => _syncStatusController.stream;
  
  /// 是否正在同步
  bool get isSyncing => _isSyncing;
  
  /// 最后同步时间
  DateTime? get lastSyncTime => _lastSyncTime;
  
  /// 初始化同步管理器
  Future<void> initialize() async {
    // 读取上次同步时间
    try {
      final lastSyncTimeStr = await _database.rawQuery(
        'SELECT value FROM app_settings WHERE key = "last_sync_time"'
      );
      
      if (lastSyncTimeStr.isNotEmpty) {
        _lastSyncTime = DateTime.parse(lastSyncTimeStr.first['value'] as String);
      }
    } catch (e) {
      // 忽略错误，可能是首次运行
      debugPrint('读取上次同步时间出错: $e');
    }
    
    // 初始化同步计划
    _scheduleSyncTask();
  }
  
  /// 安排同步任务
  void _scheduleSyncTask() {
    _syncTimer?.cancel();
    _syncTimer = Timer.periodic(_syncInterval, (_) {
      syncAll();
    });
  }
  
  /// 设置同步间隔
  void setSyncInterval(Duration interval) {
    _syncInterval = interval;
    _scheduleSyncTask();
  }
  
  /// 同步所有数据
  Future<bool> syncAll() async {
    if (_isSyncing) return false;
    
    _isSyncing = true;
    _syncStatusController.add(SyncStatus.syncing);
    
    try {
      // 同步体质评估数据
      await _syncConstitutionResults();
      
      // 同步健康调理方案数据
      await _syncHealthRegimens();
      
      // 同步四诊数据
      await _syncDiagnosticData();
      
      // 更新同步时间
      _lastSyncTime = DateTime.now();
      await _saveLastSyncTime();
      
      _syncStatusController.add(SyncStatus.succeeded);
      return true;
    } catch (e) {
      _syncStatusController.add(SyncStatus.failed);
      return false;
    } finally {
      _isSyncing = false;
    }
  }
  
  /// 同步体质评估结果
  Future<void> _syncConstitutionResults() async {
    // 上传本地新数据
    final localResults = await _database.query(
      'constitution_results',
      where: 'sync_status = ?',
      whereArgs: ['pending'],
    );
    
    for (final result in localResults) {
      try {
        await _apiClient.post('/constitution/results', data: result);
        
        // 更新同步状态
        await _database.update(
          'constitution_results',
          {'sync_status': 'synced'},
          where: 'id = ?',
          whereArgs: [result['id']],
        );
      } catch (e) {
        // 忽略错误，继续同步其他数据
        debugPrint('上传体质评估结果出错: $e');
      }
    }
    
    // 获取远程数据
    try {
      final remoteResults = await _apiClient.get('/constitution/results');
      
      // 批量更新或插入
      await _database.batch((batch) {
        for (final result in remoteResults) {
          batch.insert(
            'constitution_results',
            result,
            conflictAlgorithm: ConflictAlgorithm.replace,
          );
        }
      });
    } catch (e) {
      // 忽略错误
      debugPrint('获取远程体质评估结果出错: $e');
    }
  }
  
  /// 同步健康调理方案
  Future<void> _syncHealthRegimens() async {
    // 上传本地新数据
    final localRegimens = await _database.query(
      'health_regimens',
      where: 'sync_status = ?',
      whereArgs: ['pending'],
    );
    
    for (final regimen in localRegimens) {
      try {
        await _apiClient.post('/health/regimens', data: regimen);
        
        // 更新同步状态
        await _database.update(
          'health_regimens',
          {'sync_status': 'synced'},
          where: 'id = ?',
          whereArgs: [regimen['id']],
        );
      } catch (e) {
        // 忽略错误，继续同步其他数据
        debugPrint('上传健康调理方案出错: $e');
      }
    }
    
    // 获取远程数据
    try {
      final remoteRegimens = await _apiClient.get('/health/regimens');
      
      // 批量更新或插入
      await _database.batch((batch) {
        for (final regimen in remoteRegimens) {
          batch.insert(
            'health_regimens',
            regimen,
            conflictAlgorithm: ConflictAlgorithm.replace,
          );
        }
      });
    } catch (e) {
      // 忽略错误
      debugPrint('获取远程健康调理方案出错: $e');
    }
  }
  
  /// 同步四诊数据
  Future<void> _syncDiagnosticData() async {
    // 上传本地新数据
    final localData = await _database.query(
      'diagnostic_data',
      where: 'sync_status = ?',
      whereArgs: ['pending'],
    );
    
    for (final data in localData) {
      try {
        await _apiClient.post('/diagnostic/data', data: data);
        
        // 更新同步状态
        await _database.update(
          'diagnostic_data',
          {'sync_status': 'synced'},
          where: 'id = ?',
          whereArgs: [data['id']],
        );
      } catch (e) {
        // 忽略错误，继续同步其他数据
        debugPrint('上传四诊数据出错: $e');
      }
    }
    
    // 获取远程数据
    try {
      final remoteData = await _apiClient.get('/diagnostic/data');
      
      // 批量更新或插入
      await _database.batch((batch) {
        for (final data in remoteData) {
          batch.insert(
            'diagnostic_data',
            data,
            conflictAlgorithm: ConflictAlgorithm.replace,
          );
        }
      });
    } catch (e) {
      // 忽略错误
      debugPrint('获取远程四诊数据出错: $e');
    }
  }
  
  /// 保存最后同步时间
  Future<void> _saveLastSyncTime() async {
    if (_lastSyncTime == null) return;
    
    try {
      await _database.rawQuery(
        'INSERT OR REPLACE INTO app_settings (key, value) VALUES (?, ?)',
        ['last_sync_time', _lastSyncTime!.toIso8601String()],
      );
    } catch (e) {
      // 忽略错误
      debugPrint('保存同步时间出错: $e');
    }
  }
  
  /// 销毁同步管理器
  void dispose() {
    _syncTimer?.cancel();
    _syncStatusController.close();
  }
} 