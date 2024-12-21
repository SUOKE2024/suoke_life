import 'package:get/get.dart';
import 'package:suoke_life/services/sync_service.dart';

class SyncController extends GetxController {
  final SyncService _syncService = Get.find();

  // 同步状态
  RxBool get isSyncing => _syncService.isSyncing;
  
  // 最后同步时间
  Rxn<DateTime> get lastSyncTime => _syncService.lastSyncTime;

  // 同步范围设置
  final _syncRanges = {
    'lifeRecord': true,
    'tags': true,
    'aiChat': true,
    'analytics': true,
    'settings': true,
  }.obs;

  // 获取同步范围设置
  bool getSyncRange(String key) => _syncRanges[key] ?? false;

  // 设置同步范围
  Future<void> setSyncRange(String key, bool value) async {
    _syncRanges[key] = value;
    // TODO: 保存到设置服务
  }

  // 检查是否需要同步某个类型
  bool shouldSync(String key) => _syncRanges[key] ?? false;

  // 开始同步
  Future<void> startSync() async {
    if (isSyncing.value) {
      Get.snackbar('提示', '正在同步中，请稍候...');
      return;
    }

    try {
      await _syncService.startSync();
      Get.snackbar('成功', '数据同步完成');
    } catch (e) {
      Get.snackbar('错误', '数据同步失败: $e');
    }
  }

  // 检查是否需要同步
  bool needsSync() {
    return _syncService.needsSync();
  }

  // 自动同步
  Future<void> autoSync() async {
    if (needsSync()) {
      await startSync();
    }
  }

  // 获取同步状态文本
  String getSyncStatusText() {
    if (isSyncing.value) {
      return '正在同步...';
    }
    if (lastSyncTime.value == null) {
      return '未同步';
    }
    return '上次同步: ${_formatDateTime(lastSyncTime.value!)}';
  }

  // 格式化日期时间
  String _formatDateTime(DateTime dateTime) {
    final now = DateTime.now();
    final difference = now.difference(dateTime);

    if (difference.inMinutes < 1) {
      return '刚刚';
    } else if (difference.inHours < 1) {
      return '${difference.inMinutes}分钟前';
    } else if (difference.inDays < 1) {
      return '${difference.inHours}小时前';
    } else if (difference.inDays < 30) {
      return '${difference.inDays}天前';
    } else {
      return '${dateTime.year}-${dateTime.month}-${dateTime.day}';
    }
  }
} 