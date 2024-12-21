import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:suoke_life/presentation/controllers/search_controller.dart';

class SearchHistoryPage extends GetView<SearchController> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: TextField(
          onChanged: controller.onSearchChanged,
          autofocus: true,
          decoration: InputDecoration(
            hintText: '搜索记录...',
            border: InputBorder.none,
            prefixIcon: Icon(Icons.search),
            suffixIcon: IconButton(
              icon: Icon(Icons.clear),
              onPressed: () => controller.clearSearch(),
            ),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Get.back(),
            child: Text('取消'),
          ),
        ],
      ),
      body: Obx(() => ListView(
        children: [
          // 搜索历史
          if (controller.searchHistory.isNotEmpty) ...[
            _buildSection(
              title: '搜索历史',
              trailing: TextButton(
                onPressed: () => _showClearHistoryDialog(context),
                child: Text('清空'),
              ),
              children: controller.searchHistory.map((query) => ListTile(
                leading: Icon(Icons.history),
                title: Text(query),
                trailing: IconButton(
                  icon: Icon(Icons.close),
                  onPressed: () => controller.removeSearchHistory(query),
                ),
                onTap: () => controller.onHistoryTap(query),
              )).toList(),
            ),
            Divider(height: 1),
          ],

          // 热门搜索
          if (controller.hotSearches.isNotEmpty) ...[
            _buildSection(
              title: '热门搜索',
              children: _buildHotSearches(),
            ),
            Divider(height: 1),
          ],

          // 搜索建议
          if (controller.searchSuggestions.isNotEmpty) ...[
            _buildSection(
              title: '搜索建议',
              children: controller.searchSuggestions.map((suggestion) => ListTile(
                leading: Icon(Icons.search),
                title: Text(suggestion),
                onTap: () => controller.onSuggestionTap(suggestion),
              )).toList(),
            ),
          ],
        ],
      )),
    );
  }

  List<Widget> _buildHotSearches() {
    return [
      Padding(
        padding: EdgeInsets.symmetric(horizontal: 16),
        child: Wrap(
          spacing: 8,
          runSpacing: 8,
          children: controller.hotSearches.asMap().entries.map((entry) {
            final index = entry.key;
            final query = entry.value;
            return ActionChip(
              avatar: index < 3 ? Icon(
                Icons.local_fire_department,
                color: [Colors.red, Colors.orange, Colors.amber][index],
              ) : null,
              label: Text(query),
              onPressed: () => controller.onHistoryTap(query),
            );
          }).toList(),
        ),
      ),
      SizedBox(height: 16),
    ];
  }

  Widget _buildSection({
    required String title,
    required List<Widget> children,
    Widget? trailing,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: EdgeInsets.fromLTRB(16, 16, 16, 8),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                title,
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: Colors.grey[600],
                ),
              ),
              if (trailing != null) trailing,
            ],
          ),
        ),
        ...children,
      ],
    );
  }

  void _showClearHistoryDialog(BuildContext context) {
    Get.dialog(
      AlertDialog(
        title: Text('清空搜索历史'),
        content: Text('确定要清空所有搜索历史吗？'),
        actions: [
          TextButton(
            onPressed: () => Get.back(),
            child: Text('取消'),
          ),
          TextButton(
            onPressed: () {
              controller.clearSearchHistory();
              Get.back();
            },
            child: Text(
              '确定',
              style: TextStyle(color: Colors.red),
            ),
          ),
        ],
      ),
    );
  }
} 