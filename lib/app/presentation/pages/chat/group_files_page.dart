import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/group_files_controller.dart';
import '../../../core/base/base_page.dart';
import '../../widgets/chat/file_list_item.dart';

class GroupFilesPage extends BasePage<GroupFilesController> {
  const GroupFilesPage({Key? key}) : super(key: key);

  @override
  PreferredSizeWidget buildAppBar(BuildContext context) {
    return AppBar(
      title: const Text('群文件'),
      actions: [
        IconButton(
          icon: const Icon(Icons.upload_file),
          onPressed: controller.uploadFile,
        ),
        PopupMenuButton<String>(
          onSelected: controller.onSortMethodChanged,
          itemBuilder: (context) => [
            const PopupMenuItem(value: 'time', child: Text('按时间排序')),
            const PopupMenuItem(value: 'size', child: Text('按大小排序')),
            const PopupMenuItem(value: 'name', child: Text('按名称排序')),
            const PopupMenuItem(value: 'type', child: Text('按类型排序')),
          ],
        ),
      ],
    );
  }

  @override
  Widget buildBody(BuildContext context) {
    return Column(
      children: [
        // 文件类型过滤器
        Container(
          padding: const EdgeInsets.all(8),
          child: SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: [
                _buildFilterChip('全部', 'all'),
                _buildFilterChip('图片', 'image'),
                _buildFilterChip('视频', 'video'),
                _buildFilterChip('文档', 'document'),
                _buildFilterChip('音频', 'audio'),
                _buildFilterChip('其他', 'other'),
              ],
            ),
          ),
        ),

        // 存储空间使用情况
        Obx(() => Container(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('存储空间: ${controller.formatFileSize(controller.usedSpace.value)}'),
                  Text('剩余: ${controller.formatFileSize(controller.remainingSpace.value)}'),
                ],
              ),
              const SizedBox(height: 8),
              LinearProgressIndicator(
                value: controller.spaceUsagePercent,
                backgroundColor: Colors.grey[200],
              ),
            ],
          ),
        )),

        // 文件列表
        Expanded(
          child: Obx(() {
            if (controller.isLoading.value) {
              return const Center(child: CircularProgressIndicator());
            }
            if (controller.files.isEmpty) {
              return const Center(child: Text('暂无文件'));
            }
            return ListView.builder(
              itemCount: controller.files.length,
              itemBuilder: (context, index) {
                final file = controller.files[index];
                return FileListItem(
                  file: file,
                  onTap: () => controller.openFile(file),
                  onDownload: () => controller.downloadFile(file),
                  onDelete: () => controller.showDeleteConfirm(file),
                );
              },
            );
          }),
        ),
      ],
    );
  }

  Widget _buildFilterChip(String label, String type) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 4),
      child: Obx(() => FilterChip(
        label: Text(label),
        selected: controller.selectedFileType.value == type,
        onSelected: (selected) {
          if (selected) {
            controller.selectedFileType.value = type;
          }
        },
      )),
    );
  }
} 