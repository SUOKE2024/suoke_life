import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:suoke_life/presentation/controllers/life_controller.dart';
import 'package:suoke_life/app/core/widgets/empty_placeholder.dart';
import 'package:suoke_life/data/models/life_record.dart';
import 'package:suoke_life/services/auth_service.dart';

class LifePage extends GetView<LifeController> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('生活记录'),
        actions: [
          IconButton(
            icon: Icon(Icons.person),
            onPressed: () => controller.showUserProfile(Get.find<AuthService>().currentUser.value?.id ?? ''),
          ),
          IconButton(
            icon: Icon(Icons.tag),
            onPressed: controller.manageTag,
          ),
          IconButton(
            icon: Icon(Icons.analytics_outlined),
            onPressed: controller.showAnalytics,
          ),
          PopupMenuButton<String>(
            onSelected: _handleMenuAction,
            itemBuilder: (context) => [
              PopupMenuItem(
                value: 'export',
                child: Text('导出数据'),
              ),
              PopupMenuItem(
                value: 'search',
                child: Text('搜索历史'),
              ),
            ],
          ),
        ],
      ),
      body: Obx(() {
        if (controller.isLoading.value) {
          return Center(child: CircularProgressIndicator());
        }

        if (controller.records.isEmpty) {
          return EmptyPlaceholder(
            message: '暂无记录',
            action: TextButton(
              onPressed: controller.addRecord,
              child: Text('添加记录'),
            ),
          );
        }

        return RefreshIndicator(
          onRefresh: controller.refreshRecords,
          child: ListView.builder(
            padding: EdgeInsets.all(16),
            itemCount: controller.records.length,
            itemBuilder: (context, index) {
              final record = controller.records[index];
              return _buildRecordCard(record);
            },
          ),
        );
      }),
      floatingActionButton: FloatingActionButton(
        onPressed: controller.addRecord,
        child: Icon(Icons.add),
      ),
    );
  }

  Widget _buildRecordCard(LifeRecord record) {
    return Card(
      margin: EdgeInsets.only(bottom: 16),
      child: InkWell(
        onTap: () => controller.showRecordDetail(record.id),
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(
                      record.title,
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  Text(
                    _formatTime(record.time),
                    style: TextStyle(
                      color: Colors.grey[600],
                      fontSize: 14,
                    ),
                  ),
                ],
              ),
              if (record.content != null) ...[
                SizedBox(height: 8),
                Text(
                  record.content!,
                  maxLines: 3,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(
                    color: Colors.grey[600],
                    fontSize: 14,
                  ),
                ),
              ],
              if (record.tags.isNotEmpty) ...[
                SizedBox(height: 8),
                Wrap(
                  spacing: 8,
                  children: record.tags.map((tag) => Chip(
                    label: Text(tag),
                    materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                  )).toList(),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  String _formatTime(String time) {
    final date = DateTime.parse(time);
    final now = DateTime.now();
    final diff = now.difference(date);

    if (diff.inMinutes < 1) {
      return '刚刚';
    } else if (diff.inHours < 1) {
      return '${diff.inMinutes}分钟前';
    } else if (diff.inDays < 1) {
      return '${diff.inHours}小时前';
    } else if (diff.inDays < 30) {
      return '${diff.inDays}天前';
    } else {
      return '${date.year}-${date.month}-${date.day}';
    }
  }

  void _handleMenuAction(String action) {
    switch (action) {
      case 'export':
        controller.exportData();
        break;
      case 'search':
        controller.searchHistory();
        break;
    }
  }
} 