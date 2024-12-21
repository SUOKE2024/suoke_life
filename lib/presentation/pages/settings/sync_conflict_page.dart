import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:suoke_life/services/sync_log_service.dart';
import 'package:suoke_life/data/models/sync_conflict.dart';
import 'package:suoke_life/app/core/widgets/custom_card.dart';
import 'package:intl/intl.dart';

class SyncConflictPage extends GetView<SyncLogService> {
  final dateFormat = DateFormat('yyyy-MM-dd HH:mm:ss');

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('同步冲突'),
      ),
      body: Obx(() {
        final conflicts = controller.getUnresolvedConflicts();
        if (conflicts.isEmpty) {
          return Center(
            child: Text(
              '暂无未解决的冲突',
              style: TextStyle(color: Colors.grey[600]),
            ),
          );
        }

        return ListView.builder(
          padding: EdgeInsets.all(16),
          itemCount: conflicts.length,
          itemBuilder: (context, index) => _buildConflictCard(conflicts[index]),
        );
      }),
    );
  }

  Widget _buildConflictCard(SyncConflict conflict) {
    return CustomCard(
      margin: EdgeInsets.only(bottom: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 冲突类型和时间
          ListTile(
            title: Text(_getConflictTypeName(conflict.type)),
            subtitle: Text('发生时间：${dateFormat.format(conflict.localTime)}'),
            trailing: _buildStatusChip(conflict.resolved),
          ),
          Divider(height: 1),

          // 本地数据和服务器数据对比
          Padding(
            padding: EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '数据对比',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                SizedBox(height: 16),
                _buildDataCompare(conflict),
              ],
            ),
          ),

          // 解决按钮
          if (!conflict.resolved)
            Padding(
              padding: EdgeInsets.all(16),
              child: Row(
                children: [
                  Expanded(
                    child: OutlinedButton(
                      onPressed: () => _resolveConflict(
                        conflict,
                        useLocal: true,
                      ),
                      child: Text('使用本地版本'),
                    ),
                  ),
                  SizedBox(width: 16),
                  Expanded(
                    child: ElevatedButton(
                      onPressed: () => _resolveConflict(
                        conflict,
                        useLocal: false,
                      ),
                      child: Text('使用服务器版本'),
                    ),
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildDataCompare(SyncConflict conflict) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                '本地版本',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  color: Colors.blue,
                ),
              ),
              SizedBox(height: 8),
              _buildDataView(conflict.localData),
              Text(
                dateFormat.format(conflict.localTime),
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.grey[600],
                ),
              ),
            ],
          ),
        ),
        Container(
          width: 1,
          height: 120,
          margin: EdgeInsets.symmetric(horizontal: 16),
          color: Colors.grey[300],
        ),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                '服务器版本',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  color: Colors.green,
                ),
              ),
              SizedBox(height: 8),
              _buildDataView(conflict.serverData),
              Text(
                dateFormat.format(conflict.serverTime),
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.grey[600],
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildDataView(Map<String, dynamic> data) {
    // TODO: 根据不同类型的数据实现对应的展示方式
    return Text(data.toString());
  }

  Widget _buildStatusChip(bool resolved) {
    return Chip(
      label: Text(
        resolved ? '已解决' : '待处理',
        style: TextStyle(
          color: Colors.white,
          fontSize: 12,
        ),
      ),
      backgroundColor: resolved ? Colors.green : Colors.orange,
      padding: EdgeInsets.symmetric(horizontal: 8),
      materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
    );
  }

  String _getConflictTypeName(String type) {
    switch (type) {
      case 'life_record':
        return '生活记录';
      case 'tags':
        return '标签管理';
      case 'settings':
        return '应用设置';
      case 'feedback':
        return '反馈记录';
      default:
        return type;
    }
  }

  Future<void> _resolveConflict(
    SyncConflict conflict, {
    required bool useLocal,
  }) async {
    try {
      await controller.resolveConflict(
        conflict.id,
        resolution: useLocal ? 'use_local' : 'use_server',
      );
      Get.snackbar('成功', '已解决同步冲突');
    } catch (e) {
      Get.snackbar('错误', '解决冲突失败: $e');
    }
  }
} 