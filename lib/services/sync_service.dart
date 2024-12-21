import 'package:get/get.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:suoke_life/services/settings_service.dart';
import 'package:suoke_life/services/life_record_service.dart';
import 'package:suoke_life/services/feedback_service.dart';
import 'package:suoke_life/data/models/sync_config.dart';
import 'package:hive/hive.dart';
import 'package:suoke_life/services/sync_log_service.dart';

class SyncService extends GetxService {
  final ISettingsService _settingsService = Get.find();
  final LifeRecordService _recordService = Get.find();
  final FeedbackService _feedbackService = Get.find();
  final _connectivity = Connectivity();
  final SyncLogService _logService = Get.find();
  
  late Box<SyncConfig> _configBox;
  
  // 同步状态
  final isSyncing = false.obs;
  final syncProgress = 0.0.obs;
  final currentSyncItem = ''.obs;
  final syncError = Rxn<String>();
  
  // 网络状态
  final isWifiConnected = false.obs;
  
  @override
  Future<void> onInit() async {
    super.onInit();
    await _initHive();
    await _initConnectivity();
    _setupConnectivityStream();
  }

  Future<void> _initHive() async {
    _configBox = await Hive.openBox<SyncConfig>('sync_config');
    if (_configBox.isEmpty) {
      await _configBox.put('config', SyncConfig());
    }
  }

  // 初始化网络状态
  Future<void> _initConnectivity() async {
    try {
      final result = await _connectivity.checkConnectivity();
      _updateConnectionStatus(result);
    } catch (e) {
      print('Failed to get connectivity: $e');
    }
  }

  // 监听网络状态变化
  void _setupConnectivityStream() {
    _connectivity.onConnectivityChanged.listen((result) {
      _updateConnectionStatus(result);
      _checkAutoSync();
    });
  }

  // 更新网络状态
  void _updateConnectionStatus(ConnectivityResult result) {
    isWifiConnected.value = result == ConnectivityResult.wifi;
  }

  // 检查是否需要自动同步
  Future<void> _checkAutoSync() async {
    final config = getSyncConfig();
    if (config.autoSync && (!config.wifiOnlySync || isWifiConnected.value)) {
      await startSync();
    }
  }

  // 开始同步
  Future<void> startSync() async {
    if (isSyncing.value) return;
    
    try {
      isSyncing.value = true;
      syncError.value = null;

      // 获取同步范围
      final config = getSyncConfig();
      
      // 同步每个范围的数据
      for (final range in config.syncRanges) {
        await _syncRange(range);
      }

      // 更新同步时间
      await updateSyncConfig(config.copyWith(
        lastSyncTime: DateTime.now(),
      ));
      
    } catch (e) {
      syncError.value = '同步失败: $e';
    } finally {
      isSyncing.value = false;
    }
  }

  // 同步指定范围的数据
  Future<void> _syncRange(String range) async {
    switch (range) {
      case 'life_records':
        await _syncLifeRecords();
        break;
      case 'tags':
        await _syncTags();
        break;
      case 'settings':
        await _syncSettings();
        break;
      case 'feedback':
        await _syncFeedback();
        break;
    }
  }

  // 同步生活记录
  Future<void> _syncLifeRecords() async {
    try {
      currentSyncItem.value = '生活记录';
      syncProgress.value = 0.2;

      // 获取本地记录
      final localRecords = _recordService.getAllRecords();
      
      // 获取服务器记录（模拟）
      await Future.delayed(Duration(milliseconds: 500));
      syncProgress.value = 0.4;
      
      // 检测冲突（示例）
      for (final record in localRecords) {
        if (_hasConflict(record)) {
          await _logService.logConflict(
            type: 'life_record',
            localTime: DateTime.parse(record.time),
            serverTime: DateTime.now(), // 实际应该是服务器记录的时间
            localData: {'record': record},
            serverData: {'record': 'server_record'}, // 实际应该是服务器的记录
          );
        }
      }
      
      syncProgress.value = 0.6;
      
      // 记录同步日志
      await _logService.logSync(
        type: 'life_records',
        success: true,
        details: {
          'total': localRecords.length,
          'synced': localRecords.length,
        },
      );
      
      syncProgress.value = 1.0;
      
    } catch (e) {
      await _logService.logSync(
        type: 'life_records',
        success: false,
        error: e.toString(),
      );
      throw '同步生活记录失败: $e';
    }
  }

  // 检测记录是否有冲突（示例）
  bool _hasConflict(dynamic record) {
    // TODO: 实现实际的冲突检测逻辑
    return false;
  }

  // 同步标签
  Future<void> _syncTags() async {
    try {
      currentSyncItem.value = '标签管理';
      syncProgress.value = 0.3;
      
      // 获取本地标签
      await Future.delayed(Duration(milliseconds: 200));
      syncProgress.value = 0.6;
      
      // 同步标签（模拟）
      await Future.delayed(Duration(milliseconds: 300));
      syncProgress.value = 1.0;
      
    } catch (e) {
      throw '同步标签失败: $e';
    }
  }

  // 同步设置
  Future<void> _syncSettings() async {
    try {
      currentSyncItem.value = '应用设置';
      syncProgress.value = 0.5;
      
      // 同步设置（模拟）
      await Future.delayed(Duration(milliseconds: 300));
      syncProgress.value = 1.0;
      
    } catch (e) {
      throw '同步设置失败: $e';
    }
  }

  // 同步反馈
  Future<void> _syncFeedback() async {
    try {
      currentSyncItem.value = '反馈记录';
      syncProgress.value = 0.4;
      
      // 获取本地反馈
      final localFeedback = _feedbackService.getFeedbackHistory();
      
      // 同步反馈（模拟）
      await Future.delayed(Duration(milliseconds: 200));
      syncProgress.value = 1.0;
      
    } catch (e) {
      throw '同步反馈失败: $e';
    }
  }

  // 更新同步配置
  Future<void> updateSyncConfig(SyncConfig config) async {
    await _configBox.put('config', config);
  }

  // 获取同步配置
  SyncConfig getSyncConfig() {
    return _configBox.get('config') ?? SyncConfig();
  }
} 