import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:suoke_life/core/sync/sync_manager.dart';
import 'package:suoke_life/di/providers.dart';

/// 同步状态小部件
class SyncStatusWidget extends ConsumerWidget {
  const SyncStatusWidget({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final syncStatusAsync = ref.watch(syncStatusProvider);
    final lastSyncTime = ref.watch(lastSyncTimeProvider);
    final syncManager = ref.watch(syncManagerProvider);

    return Card(
      margin: const EdgeInsets.all(8),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              '数据同步状态',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            syncStatusAsync.when(
              data: (syncStatus) => Row(
                children: [
                  _buildStatusIcon(syncStatus),
                  const SizedBox(width: 8),
                  Text(
                    _getStatusText(syncStatus),
                    style: TextStyle(
                      color: _getStatusColor(syncStatus),
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
              loading: () => const Row(
                children: [
                  SizedBox(
                    width: 24,
                    height: 24,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                    ),
                  ),
                  SizedBox(width: 8),
                  Text('加载中...'),
                ],
              ),
              error: (error, stack) => Row(
                children: [
                  Icon(Icons.error, color: Colors.red),
                  SizedBox(width: 8),
                  Text(
                    '状态加载错误',
                    style: TextStyle(
                      color: Colors.red,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ),
            if (lastSyncTime != null) ...[
              const SizedBox(height: 8),
              Text(
                '上次同步: ${_formatDateTime(lastSyncTime)}',
                style: const TextStyle(
                  fontSize: 14,
                  color: Colors.grey,
                ),
              ),
            ],
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                OutlinedButton.icon(
                  onPressed: syncStatusAsync.maybeWhen(
                    data: (status) => status == SyncStatus.syncing ? null : () => syncManager.syncAll(),
                    orElse: () => null,
                  ),
                  icon: const Icon(Icons.sync),
                  label: const Text('立即同步'),
                ),
                TextButton.icon(
                  onPressed: () {
                    showDialog(
                      context: context,
                      builder: (context) => const _SyncDetailsDialog(),
                    );
                  },
                  icon: const Icon(Icons.info_outline),
                  label: const Text('同步详情'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusIcon(SyncStatus status) {
    switch (status) {
      case SyncStatus.idle:
        return const Icon(Icons.hourglass_empty, color: Colors.grey);
      case SyncStatus.syncing:
        return const SizedBox(
          width: 24,
          height: 24,
          child: CircularProgressIndicator(
            strokeWidth: 2,
            valueColor: AlwaysStoppedAnimation<Color>(Colors.blue),
          ),
        );
      case SyncStatus.succeeded:
        return const Icon(Icons.check_circle, color: Colors.green);
      case SyncStatus.failed:
        return const Icon(Icons.error, color: Colors.red);
      case SyncStatus.noConnection:
        return const Icon(Icons.signal_wifi_off, color: Colors.orange);
    }
  }

  String _getStatusText(SyncStatus status) {
    switch (status) {
      case SyncStatus.idle:
        return '等待同步';
      case SyncStatus.syncing:
        return '同步中...';
      case SyncStatus.succeeded:
        return '同步成功';
      case SyncStatus.failed:
        return '同步失败';
      case SyncStatus.noConnection:
        return '无网络连接';
    }
  }

  Color _getStatusColor(SyncStatus status) {
    switch (status) {
      case SyncStatus.idle:
        return Colors.grey;
      case SyncStatus.syncing:
        return Colors.blue;
      case SyncStatus.succeeded:
        return Colors.green;
      case SyncStatus.failed:
        return Colors.red;
      case SyncStatus.noConnection:
        return Colors.orange;
    }
  }

  String _formatDateTime(DateTime dateTime) {
    final now = DateTime.now();
    final difference = now.difference(dateTime);

    if (difference.inDays > 0) {
      return DateFormat('yyyy-MM-dd HH:mm').format(dateTime);
    } else if (difference.inHours > 0) {
      return '${difference.inHours}小时前';
    } else if (difference.inMinutes > 0) {
      return '${difference.inMinutes}分钟前';
    } else {
      return '刚刚';
    }
  }
}

/// 同步详情对话框
class _SyncDetailsDialog extends ConsumerWidget {
  const _SyncDetailsDialog();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final syncManager = ref.watch(syncManagerProvider);
    final lastSyncTime = ref.watch(lastSyncTimeProvider);

    return AlertDialog(
      title: const Text('同步详情'),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (lastSyncTime != null) ...[
            Text('上次同步时间: ${DateFormat('yyyy-MM-dd HH:mm:ss').format(lastSyncTime)}'),
            const SizedBox(height: 8),
          ],
          const Text('同步数据类型:'),
          const SizedBox(height: 4),
          _buildSyncTypeItem('健康数据', Icons.favorite, Colors.red),
          _buildSyncTypeItem('诊断结果', Icons.medical_services, Colors.blue),
          _buildSyncTypeItem('知识数据', Icons.book, Colors.green),
          _buildSyncTypeItem('配置数据', Icons.settings, Colors.purple),
        ],
      ),
      actions: [
        TextButton(
          onPressed: () {
            Navigator.of(context).pop();
          },
          child: const Text('关闭'),
        ),
        ElevatedButton(
          onPressed: () {
            syncManager.syncAll();
            Navigator.of(context).pop();
          },
          child: const Text('立即同步'),
        ),
      ],
    );
  }

  Widget _buildSyncTypeItem(String title, IconData icon, Color color) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        children: [
          Icon(icon, color: color, size: 20),
          const SizedBox(width: 8),
          Text(title),
        ],
      ),
    );
  }
} 