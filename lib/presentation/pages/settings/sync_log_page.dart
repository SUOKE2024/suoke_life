import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:suoke_life/services/sync_log_service.dart';
import 'package:suoke_life/data/models/sync_log.dart';
import 'package:suoke_life/app/core/widgets/custom_card.dart';
import 'package:intl/intl.dart';

class SyncLogPage extends GetView<SyncLogService> {
  final dateFormat = DateFormat('yyyy-MM-dd HH:mm:ss');

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('同步日志'),
        actions: [
          PopupMenuButton<String>(
            onSelected: _handleMenuAction,
            itemBuilder: (context) => [
              PopupMenuItem(
                value: 'filter',
                child: Text('筛选'),
              ),
              PopupMenuItem(
                value: 'export',
                child: Text('导出'),
              ),
              PopupMenuItem(
                value: 'clean',
                child: Text('清理'),
              ),
            ],
          ),
        ],
      ),
      body: Obx(() {
        final logs = controller.getLogs();
        if (logs.isEmpty) {
          return Center(
            child: Text(
              '暂无同步日志',
              style: TextStyle(color: Colors.grey[600]),
            ),
          );
        }

        return ListView.builder(
          padding: EdgeInsets.all(16),
          itemCount: logs.length,
          itemBuilder: (context, index) => _buildLogCard(logs[index]),
        );
      }),
    );
  }

  Widget _buildLogCard(SyncLog log) {
    return CustomCard(
      margin: EdgeInsets.only(bottom: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          ListTile(
            title: Text(_getLogTypeName(log.type)),
            subtitle: Text(dateFormat.format(log.time)),
            trailing: _buildStatusChip(log.success),
          ),
          if (log.error != null)
            Container(
              padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              color: Colors.red[50],
              child: Row(
                children: [
                  Icon(Icons.error_outline, color: Colors.red, size: 16),
                  SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      log.error!,
                      style: TextStyle(
                        color: Colors.red,
                        fontSize: 12,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          if (log.details != null)
            Padding(
              padding: EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '详细信息',
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  SizedBox(height: 8),
                  _buildDetailsView(log.details!),
                ],
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildDetailsView(Map<String, dynamic> details) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: details.entries.map((entry) {
        return Padding(
          padding: EdgeInsets.only(bottom: 4),
          child: Text(
            '${entry.key}: ${entry.value}',
            style: TextStyle(fontSize: 12),
          ),
        );
      }).toList(),
    );
  }

  Widget _buildStatusChip(bool success) {
    return Chip(
      label: Text(
        success ? '成功' : '失败',
        style: TextStyle(
          color: Colors.white,
          fontSize: 12,
        ),
      ),
      backgroundColor: success ? Colors.green : Colors.red,
      padding: EdgeInsets.symmetric(horizontal: 8),
      materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
    );
  }

  String _getLogTypeName(String type) {
    switch (type) {
      case 'life_records':
        return '生活记录同步';
      case 'tags':
        return '标签同步';
      case 'settings':
        return '设置同步';
      case 'feedback':
        return '反馈同步';
      default:
        return type;
    }
  }

  Future<void> _handleMenuAction(String action) async {
    switch (action) {
      case 'filter':
        // TODO: 实现日志筛选
        break;
      case 'export':
        // TODO: 实现日志导出
        break;
      case 'clean':
        final confirmed = await Get.dialog<bool>(
          AlertDialog(
            title: Text('清理日志'),
            content: Text('确定要清理30天前的日志吗？'),
            actions: [
              TextButton(
                onPressed: () => Get.back(result: false),
                child: Text('取消'),
              ),
              ElevatedButton(
                onPressed: () => Get.back(result: true),
                child: Text('确定'),
              ),
            ],
          ),
        );

        if (confirmed == true) {
          await controller.cleanOldLogs();
          Get.snackbar('成功', '已清理旧日志');
        }
        break;
    }
  }
} 