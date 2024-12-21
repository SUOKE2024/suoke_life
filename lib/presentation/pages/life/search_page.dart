import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:suoke_life/presentation/controllers/search_controller.dart';
import 'package:suoke_life/data/models/life_record.dart';

class SearchPage extends GetView<SearchController> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: TextField(
          onChanged: controller.onSearchChanged,
          decoration: InputDecoration(
            hintText: '搜索记录...',
            border: InputBorder.none,
            prefixIcon: Icon(Icons.search),
          ),
        ),
        actions: [
          IconButton(
            icon: Icon(Icons.filter_list),
            onPressed: () => _showFilterDialog(context),
          ),
        ],
      ),
      body: Column(
        children: [
          // 已选标签
          Obx(() => controller.selectedTags.isEmpty
            ? SizedBox()
            : Container(
                padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                child: Wrap(
                  spacing: 8,
                  children: controller.selectedTags.map((tag) => Chip(
                    label: Text(tag),
                    onDeleted: () => controller.toggleTag(tag),
                  )).toList(),
                ),
              ),
          ),
          
          // 搜索结果
          Expanded(
            child: Obx(() => ListView.builder(
              itemCount: controller.filteredRecords.length,
              itemBuilder: (context, index) {
                final record = controller.filteredRecords[index];
                return _buildRecordItem(record);
              },
            )),
          ),
        ],
      ),
    );
  }

  Widget _buildRecordItem(LifeRecord record) {
    return ListTile(
      title: Text(record.content),
      subtitle: Text(record.time),
      trailing: record.tags.isEmpty ? null : Wrap(
        children: record.tags.map((tag) => Chip(
          label: Text(tag),
        )).toList(),
      ),
      onTap: () => controller.onRecordTap(record),
    );
  }

  void _showFilterDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('筛选'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // 时间范围选择
            ListTile(
              title: Text('时间范围'),
              trailing: Icon(Icons.calendar_today),
              onTap: () => controller.showDateRangePicker(context),
            ),
            // 标签选择
            ListTile(
              title: Text('标签'),
              trailing: Icon(Icons.label),
              onTap: () => _showTagSelectionDialog(context),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () {
              Get.back();
              controller.clearFilters();
            },
            child: Text('清除筛选'),
          ),
          TextButton(
            onPressed: () => Get.back(),
            child: Text('确定'),
          ),
        ],
      ),
    );
  }

  void _showTagSelectionDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('选择标签'),
        content: Obx(() => Wrap(
          spacing: 8,
          children: controller.allTags.map((tag) {
            final isSelected = controller.selectedTags.contains(tag);
            return FilterChip(
              label: Text(tag),
              selected: isSelected,
              onSelected: (_) {
                controller.toggleTag(tag);
              },
            );
          }).toList(),
        )),
        actions: [
          TextButton(
            onPressed: () => Get.back(),
            child: Text('确定'),
          ),
        ],
      ),
    );
  }
} 