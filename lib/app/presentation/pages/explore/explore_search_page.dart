import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../core/base/base_page.dart';
import '../../controllers/explore_search_controller.dart';
import '../../widgets/explore_card.dart';
import '../../widgets/search_history_chip.dart';

class ExploreSearchPage extends BasePage<ExploreSearchController> {
  const ExploreSearchPage({Key? key}) : super(key: key);

  @override
  PreferredSizeWidget buildAppBar(BuildContext context) {
    return AppBar(
      title: TextField(
        controller: controller.searchController,
        autofocus: true,
        decoration: InputDecoration(
          hintText: '搜索知识、工具...',
          border: InputBorder.none,
          suffixIcon: IconButton(
            icon: const Icon(Icons.clear),
            onPressed: controller.clearSearch,
          ),
        ),
        onSubmitted: controller.onSearch,
      ),
      actions: [
        TextButton(
          onPressed: () => Get.back(),
          child: const Text('取消'),
        ),
      ],
    );
  }

  @override
  Widget buildBody(BuildContext context) {
    return Column(
      children: [
        // 搜索历史和热门搜索
        Obx(() => controller.searchText.isEmpty
          ? _buildSearchSuggestions()
          : _buildSearchResults()),
      ],
    );
  }

  Widget _buildSearchSuggestions() {
    return Expanded(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 搜索历史
            if (controller.searchHistory.isNotEmpty) ...[
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    '搜索历史',
                    style: Get.textTheme.titleMedium,
                  ),
                  TextButton(
                    onPressed: controller.clearHistory,
                    child: const Text('清空'),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: controller.searchHistory.map((keyword) {
                  return SearchHistoryChip(
                    keyword: keyword,
                    onTap: () => controller.onSearch(keyword),
                    onDelete: () => controller.removeFromHistory(keyword),
                  );
                }).toList(),
              ),
              const SizedBox(height: 24),
            ],
            
            // 热门搜索
            Text(
              '热门搜索',
              style: Get.textTheme.titleMedium,
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: controller.hotSearches.map((keyword) {
                return ActionChip(
                  label: Text(keyword),
                  onPressed: () => controller.onSearch(keyword),
                );
              }).toList(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSearchResults() {
    return Expanded(
      child: Obx(() {
        if (controller.isLoading.value) {
          return const Center(child: CircularProgressIndicator());
        }
        
        if (controller.searchResults.isEmpty) {
          return Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(
                  Icons.search_off_outlined,
                  size: 64,
                  color: Colors.grey[400],
                ),
                const SizedBox(height: 16),
                Text(
                  '未找到相关内容',
                  style: Get.textTheme.titleMedium?.copyWith(
                    color: Colors.grey[600],
                  ),
                ),
              ],
            ),
          );
        }
        
        return GridView.builder(
          padding: const EdgeInsets.all(16),
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 2,
            mainAxisSpacing: 16,
            crossAxisSpacing: 16,
            childAspectRatio: 0.8,
          ),
          itemCount: controller.searchResults.length,
          itemBuilder: (context, index) {
            final item = controller.searchResults[index];
            return ExploreCard(
              item: item,
              onTap: () => controller.showItemDetail(item),
            );
          },
        );
      }),
    );
  }
} 