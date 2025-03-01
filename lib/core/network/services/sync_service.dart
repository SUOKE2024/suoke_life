import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:uuid/uuid.dart';
import 'package:logger/logger.dart';
import '../../../data/datasources/local/database_helper.dart';
import '../../../core/database/database_schema.dart';
import '../../../core/error/exceptions.dart';
import '../../../core/network/api_client.dart';
import '../../../core/network/network_info.dart';
import '../../../data/models/sync_request_model.dart';
import '../../../data/models/sync_response_model.dart';

/// 同步状态枚举
enum SyncStatus {
  /// 待同步
  pending,
  
  /// 正在同步
  syncing,
  
  /// 已同步
  synced,
  
  /// 同步失败
  failed,
  
  /// 存在冲突
  conflict,
}

/// 同步项目
class SyncItem {
  final String table;
  final String id;
  final Map<String, dynamic> data;
  final SyncStatus status;
  final DateTime timestamp;
  final String? error;
  
  SyncItem({
    required this.table,
    required this.id,
    required this.data,
    required this.status,
    required this.timestamp,
    this.error,
  });
}

/// 同步服务
/// 负责在本地数据库和远程服务器之间同步数据
class SyncService {
  final DatabaseHelper _databaseHelper;
  final ApiClient _apiClient;
  final NetworkInfo _networkInfo;
  final Logger _logger;
  final Uuid _uuid = Uuid();
  
  /// 同步间隔
  final Duration syncInterval;
  
  /// 同步状态流控制器
  final StreamController<SyncStatus> _syncStatusController = StreamController<SyncStatus>.broadcast();
  
  /// 定时器
  Timer? _syncTimer;
  
  /// 是否正在同步
  bool _isSyncing = false;
  
  /// 构造函数
  SyncService({
    required DatabaseHelper databaseHelper,
    required ApiClient apiClient,
    required NetworkInfo networkInfo,
    required Logger logger,
    this.syncInterval = const Duration(minutes: 15),
  })  : _databaseHelper = databaseHelper,
        _apiClient = apiClient,
        _networkInfo = networkInfo,
        _logger = logger;
  
  /// 同步状态流
  Stream<SyncStatus> get syncStatusStream => _syncStatusController.stream;
  
  /// 初始化同步服务
  void initialize() {
    _logger.i('初始化同步服务');
    
    // 设置定时同步
    _syncTimer?.cancel();
    _syncTimer = Timer.periodic(syncInterval, (_) => syncData());
    
    // 监听网络状态变化
    _networkInfo.onConnectivityChanged.listen((connectivity) {
      if (connectivity != ConnectivityResult.none) {
        _logger.i('网络已恢复连接，尝试同步数据');
        syncData();
      }
    });
  }
  
  /// 同步数据
  Future<bool> syncData() async {
    // 检查是否已经在同步中
    if (_isSyncing) {
      _logger.i('同步正在进行中，跳过本次同步');
      return false;
    }
    
    // 检查网络连接
    final bool isConnected = await _networkInfo.isConnected;
    if (!isConnected) {
      _logger.w('无网络连接，无法同步数据');
      _syncStatusController.add(SyncStatus.failed);
      return false;
    }
    
    _isSyncing = true;
    _syncStatusController.add(SyncStatus.syncing);
    
    try {
      _logger.i('开始同步数据');
      
      // 同步各表数据
      await _syncTable(DatabaseSchema.tableHealthData);
      await _syncTable(DatabaseSchema.tableChatMessages);
      await _syncTable(DatabaseSchema.tableLifeRecords);
      await _syncTable(DatabaseSchema.tableHealthPlans);
      
      // 更新用户设置的最后同步时间
      await _updateLastSyncTime();
      
      _logger.i('数据同步完成');
      _syncStatusController.add(SyncStatus.synced);
      _isSyncing = false;
      return true;
    } catch (e, stackTrace) {
      _logger.e('数据同步失败', error: e, stackTrace: stackTrace);
      _syncStatusController.add(SyncStatus.failed);
      _isSyncing = false;
      return false;
    }
  }
  
  /// 同步指定表数据
  Future<void> _syncTable(String table) async {
    _logger.i('同步表: $table');
    
    try {
      // 获取待同步数据
      final List<Map<String, dynamic>> pendingData = await _databaseHelper.query(
        table,
        where: 'synced = ?',
        whereArgs: [0],
        limit: 100,
      );
      
      if (pendingData.isEmpty) {
        _logger.i('表 $table 没有待同步数据');
        return;
      }
      
      _logger.i('表 $table 有 ${pendingData.length} 条待同步数据');
      
      // 准备同步请求
      final syncRequest = SyncRequestModel(
        table: table,
        timestamp: DateTime.now().toIso8601String(),
        data: pendingData,
      );
      
      // 发送同步请求
      final response = await _apiClient.post(
        '/sync',
        data: syncRequest.toJson(),
      );
      
      // 处理同步响应
      final syncResponse = SyncResponseModel.fromJson(response.data);
      
      // 更新本地同步状态
      await _processSyncResponse(table, syncResponse);
      
    } catch (e, stackTrace) {
      _logger.e('表 $table 同步失败', error: e, stackTrace: stackTrace);
      throw SyncException(
        message: '表 $table 同步失败: $e',
        table: table,
      );
    }
  }
  
  /// 处理同步响应
  Future<void> _processSyncResponse(String table, SyncResponseModel response) async {
    final successful = response.successful;
    final failed = response.failed;
    final conflicts = response.conflicts;
    
    _logger.i('表 $table 同步结果: 成功=${successful.length}, 失败=${failed.length}, 冲突=${conflicts.length}');
    
    // 处理成功项
    if (successful.isNotEmpty) {
      await _databaseHelper.transaction((txn) async {
        for (final item in successful) {
          await txn.update(
            table,
            {'synced': 1},
            where: 'id = ?',
            whereArgs: [item['id']],
          );
        }
      });
    }
    
    // 处理失败项
    if (failed.isNotEmpty) {
      _logger.w('表 $table 有 ${failed.length} 条数据同步失败');
      // 可以选择重试或记录错误
    }
    
    // 处理冲突项
    if (conflicts.isNotEmpty) {
      _logger.w('表 $table 有 ${conflicts.length} 条数据存在冲突');
      // TODO: 实现冲突解决策略
      // 可以基于时间戳、版本号或其他策略解决冲突
    }
  }
  
  /// 更新最后同步时间
  Future<void> _updateLastSyncTime() async {
    final now = DateTime.now().millisecondsSinceEpoch;
    
    try {
      // 获取当前用户ID
      final userResult = await _databaseHelper.queryOne(
        DatabaseSchema.tableUsers,
        limit: 1,
      );
      
      if (userResult != null) {
        final userId = userResult['id'];
        
        // 更新用户设置
        await _databaseHelper.update(
          DatabaseSchema.tableUserSettings,
          {'last_sync': now},
          where: 'user_id = ?',
          whereArgs: [userId],
        );
        
        _logger.i('更新最后同步时间: ${DateTime.fromMillisecondsSinceEpoch(now)}');
      }
    } catch (e) {
      _logger.e('更新最后同步时间失败', error: e);
    }
  }
  
  /// 手动同步特定项目
  Future<bool> syncItem(String table, String id) async {
    if (!await _networkInfo.isConnected) {
      _logger.w('无网络连接，无法同步项目');
      return false;
    }
    
    try {
      _logger.i('手动同步项目: 表=$table, ID=$id');
      
      // 获取项目数据
      final item = await _databaseHelper.queryOne(
        table,
        where: 'id = ?',
        whereArgs: [id],
      );
      
      if (item == null) {
        _logger.w('项目不存在: 表=$table, ID=$id');
        return false;
      }
      
      // 准备同步请求
      final syncRequest = SyncRequestModel(
        table: table,
        timestamp: DateTime.now().toIso8601String(),
        data: [item],
      );
      
      // 发送同步请求
      final response = await _apiClient.post(
        '/sync/item',
        data: syncRequest.toJson(),
      );
      
      // a处理同步响应
      final syncResponse = SyncResponseModel.fromJson(response.data);
      
      // 更新本地同步状态
      await _processSyncResponse(table, syncResponse);
      
      return syncResponse.successful.isNotEmpty;
    } catch (e) {
      _logger.e('手动同步项目失败: 表=$table, ID=$id', error: e);
      return false;
    }
  }
  
  /// 设置数据同步状态
  Future<void> markAsSynced(String table, String id) async {
    await _databaseHelper.update(
      table,
      {'synced': 1},
      where: 'id = ?',
      whereArgs: [id],
    );
  }
  
  /// 设置数据为待同步状态
  Future<void> markForSync(String table, String id) async {
    await _databaseHelper.update(
      table,
      {'synced': 0},
      where: 'id = ?',
      whereArgs: [id],
    );
  }
  
  /// 停止同步服务
  void dispose() {
    _syncTimer?.cancel();
    _syncTimer = null;
    _syncStatusController.close();
  }
}

/// 同步异常
class SyncException implements Exception {
  final String message;
  final String table;
  
  SyncException({
    required this.message,
    required this.table,
  });
  
  @override
  String toString() => 'SyncException: $message (表: $table)';
}

/// 同步服务提供者
final syncServiceProvider = Provider<SyncService>((ref) {
  final databaseHelper = ref.watch(databaseHelperProvider);
  final apiClient = ref.watch(apiClientProvider);
  final networkInfo = ref.watch(networkInfoProvider);
  final logger = Logger();
  
  final service = SyncService(
    databaseHelper: databaseHelper,
    apiClient: apiClient,
    networkInfo: networkInfo,
    logger: logger,
  );
  
  // 初始化服务
  service.initialize();
  
  // 在Provider被释放时释放资源
  ref.onDispose(() {
    service.dispose();
  });
  
  return service;
});

/// 数据库辅助类提供者
final databaseHelperProvider = Provider<DatabaseHelper>((ref) {
  return DatabaseHelper();
});

/// 同步状态提供者
final syncStatusProvider = StreamProvider<SyncStatus>((ref) {
  final syncService = ref.watch(syncServiceProvider);
  return syncService.syncStatusStream;
});