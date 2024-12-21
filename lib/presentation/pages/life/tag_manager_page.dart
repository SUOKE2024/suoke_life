import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:suoke_life/presentation/controllers/tag_manager_controller.dart';

class TagManagerPage extends GetView<TagManagerController> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('标签管理'),
      ),
      body: Column(
        children: [
          // 添加新标签
          Padding(
            padding: EdgeInsets.all(16),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    onChanged: (value) => controller.newTag = value,
                    decoration: InputDecoration(
                      hintText: '输入新标签',
                      border: OutlineInputBorder(),
                      prefixIcon: Icon(Icons.label_outline),
                      contentPadding: EdgeInsets.symmetric(horizontal: 16),
                    ),
                  ),
                ),
                SizedBox(width: 16),
                ElevatedButton.icon(
                  onPressed: controller.addTag,
                  icon: Icon(Icons.add),
                  label: Text('添加'),
                  style: ElevatedButton.styleFrom(
                    padding: EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                  ),
                ),
              ],
            ),
          ),
          
          Divider(height: 1),
          
          // 标签列表
          Expanded(
            child: ListView(
              padding: EdgeInsets.only(bottom: 16),
              children: [
                // 自定义标签
                _buildSection(
                  title: '自定义标签',
                  icon: Icons.label,
                  tags: controller.customTags,
                  onDelete: controller.removeTag,
                  onEdit: _showEditDialog,
                ),
                
                // 推荐标签
                _buildSection(
                  title: '推荐标签',
                  icon: Icons.recommend,
                  tags: controller.recommendedTags,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildSection({
    required String title,
    required IconData icon,
    required List<String> tags,
    Function(String)? onDelete,
    Function(String)? onEdit,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: EdgeInsets.fromLTRB(16, 16, 16, 8),
          child: Row(
            children: [
              Icon(icon, size: 20),
              SizedBox(width: 8),
              Text(
                title,
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ),
        Padding(
          padding: EdgeInsets.symmetric(horizontal: 16),
          child: Obx(() => Wrap(
            spacing: 8,
            runSpacing: 8,
            children: tags.map((tag) => _buildTagChip(
              tag,
              onDelete: onDelete,
              onEdit: onEdit,
            )).toList(),
          )),
        ),
        if (tags.isNotEmpty) SizedBox(height: 16),
      ],
    );
  }
  
  Widget _buildTagChip(
    String tag, {
    Function(String)? onDelete,
    Function(String)? onEdit,
  }) {
    return ActionChip(
      label: Text(tag),
      onPressed: onEdit != null ? () => onEdit(tag) : null,
      deleteIcon: onDelete != null ? Icon(Icons.close, size: 18) : null,
      onDeleted: onDelete != null ? () => onDelete(tag) : null,
      backgroundColor: onDelete != null ? Colors.blue.shade50 : Colors.grey.shade100,
      shape: StadiumBorder(
        side: BorderSide(
          color: onDelete != null ? Colors.blue.shade200 : Colors.transparent,
        ),
      ),
    );
  }
  
  void _showEditDialog(String tag) {
    final textController = TextEditingController(text: tag);
    
    Get.dialog(
      AlertDialog(
        title: Text('编辑标签'),
        content: TextField(
          controller: textController,
          decoration: InputDecoration(
            hintText: '输入新标签名',
            border: OutlineInputBorder(),
            prefixIcon: Icon(Icons.edit),
          ),
          autofocus: true,
        ),
        actions: [
          TextButton(
            onPressed: () => Get.back(),
            child: Text('取消'),
          ),
          ElevatedButton(
            onPressed: () {
              controller.editTag(tag, textController.text);
              Get.back();
            },
            child: Text('确定'),
          ),
        ],
      ),
    );
  }
} 