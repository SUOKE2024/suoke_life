import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../core/base/base_page.dart';
import '../../controllers/explore_search_controller.dart';
import '../../widgets/explore_card.dart';
import '../../widgets/search_history_chip.dart';

class ExploreSearchPage extends GetView<ExploreSearchController> {
  const ExploreSearchPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: TextField(
          controller: controller.searchController,
          decoration: const InputDecoration(
            hintText: '搜索...',
            border: InputBorder.none,
          ),
          onSubmitted: controller.onSearch,
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.clear),
            onPressed: controller.clearSearch,
          ),
        ],
      ),
      body: Obx(() {
        if (controller.isLoading.value) {
          return const Center(child: CircularProgressIndicator());
        }
        
        if (controller.searchResults.isEmpty) {
          return const Center(child: Text('暂无搜索结果'));
        }
        
        return ListView.builder(
          itemCount: controller.searchResults.length,
          itemBuilder: (context, index) {
            final item = controller.searchResults[index];
            return ListTile(
              title: Text(item.title),
              subtitle: Text(
                item.content,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              onTap: () => controller.onItemTap(item),
            );
          },
        );
      }),
    );
  }
} 