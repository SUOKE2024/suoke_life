import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/group_search_controller.dart';
import '../../../core/base/base_page.dart';
import '../../widgets/chat/message_list_item.dart';

class GroupSearchPage extends BasePage<GroupSearchController> {
  const GroupSearchPage({Key? key}) : super(key: key);

  @override
  PreferredSizeWidget buildAppBar(BuildContext context) {
    return AppBar(
      title: TextField(
        controller: controller.searchController,
        autofocus: true,
        decoration: const InputDecoration(
          hintText: '搜索聊天记录',
          border: InputBorder.none,
        ),
        onChanged: controller.onSearchChanged,
      ),
      actions: [
        IconButton(
          icon: const Icon(Icons.filter_list),
          onPressed: controller.showFilterOptions,
        ),
      ],
    );
  }

  @override
  Widget buildBody(BuildContext context) {
    return Column(
      children: [
        // 搜索过滤器
        Obx(() {
          if (!controller.showFilter.value) return const SizedBox();
          return Card(
            margin: const EdgeInsets.all(8),
            child: Padding(
              padding: const EdgeInsets.all(8),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('搜索范围', style: TextStyle(fontWeight: FontWeight.bold)),
                  Wrap(
                    spacing: 8,
                    children: [
                      FilterChip(
                        label: const Text('文本'),
                        selected: controller.searchText.value,
                        onSelected: controller.toggleSearchText,
                      ),
                      FilterChip(
                        label: const Text('图片'),
                        selected: controller.searchImage.value,
                        onSelected: controller.toggleSearchImage,
                      ),
                      FilterChip(
                        label: const Text('文件'),
                        selected: controller.searchFile.value,
                        onSelected: controller.toggleSearchFile,
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  const Text('时间范围', style: TextStyle(fontWeight: FontWeight.bold)),
                  Row(
                    children: [
                      Expanded(
                        child: DropdownButton<String>(
                          value: controller.timeRange.value,
                          isExpanded: true,
                          items: const [
                            DropdownMenuItem(value: 'all', child: Text('全部时间')),
                            DropdownMenuItem(value: 'today', child: Text('今天')),
                            DropdownMenuItem(value: 'week', child: Text('最近一周')),
                            DropdownMenuItem(value: 'month', child: Text('最近一月')),
                          ],
                          onChanged: controller.setTimeRange,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          );
        }),

        // 搜索结果
        Expanded(
          child: Obx(() {
            if (controller.isLoading.value) {
              return const Center(child: CircularProgressIndicator());
            }
            if (controller.searchResults.isEmpty) {
              return const Center(child: Text('无搜索结果'));
            }
            return ListView.builder(
              itemCount: controller.searchResults.length,
              itemBuilder: (context, index) {
                final message = controller.searchResults[index];
                return MessageListItem(
                  message: message,
                  onTap: () => controller.onMessageTap(message),
                  showTime: true,
                  highlightText: controller.searchController.text,
                );
              },
            );
          }),
        ),
      ],
    );
  }
} 