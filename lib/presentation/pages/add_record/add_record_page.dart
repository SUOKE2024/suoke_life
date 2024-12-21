import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:suoke_life/presentation/controllers/add_record_controller.dart';
import 'package:suoke_life/widgets/custom_text_field.dart';
import 'package:suoke_life/widgets/tag_selector.dart';

class AddRecordPage extends GetView<AddRecordController> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('添加记录'),
        actions: [
          TextButton(
            onPressed: controller.saveRecord,
            child: Text('保存'),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 内容输入
            CustomTextField(
              controller: controller.contentController,
              label: '内容',
              hint: '记录此刻的想法...',
              maxLines: 5,
            ),
            SizedBox(height: 16),

            // 标签选择
            Text(
              '标签',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            SizedBox(height: 8),
            Obx(() => TagSelector(
              selectedTags: controller.selectedTags,
              onTagSelected: controller.toggleTag,
            )),
            SizedBox(height: 16),

            // 图片上传
            Text(
              '图片',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            SizedBox(height: 8),
            Obx(() => _buildImageSection()),

            // 位置信息
            if (controller.location.value != null) ...[
              SizedBox(height: 16),
              Row(
                children: [
                  Icon(Icons.location_on, size: 16),
                  SizedBox(width: 4),
                  Text(controller.location.value!),
                ],
              ),
            ],
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: controller.pickImage,
        child: Icon(Icons.camera_alt),
      ),
    );
  }

  Widget _buildImageSection() {
    if (controller.images.isEmpty) {
      return Container(
        height: 100,
        decoration: BoxDecoration(
          color: Colors.grey[200],
          borderRadius: BorderRadius.circular(8),
        ),
        child: Center(
          child: Text(
            '点击右下角按钮添加图片',
            style: TextStyle(color: Colors.grey[600]),
          ),
        ),
      );
    }

    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: [
        ...controller.images.map((image) => Stack(
          children: [
            Container(
              width: 100,
              height: 100,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(8),
                image: DecorationImage(
                  image: FileImage(image),
                  fit: BoxFit.cover,
                ),
              ),
            ),
            Positioned(
              right: 4,
              top: 4,
              child: GestureDetector(
                onTap: () => controller.removeImage(image),
                child: Container(
                  padding: EdgeInsets.all(4),
                  decoration: BoxDecoration(
                    color: Colors.black.withOpacity(0.5),
                    shape: BoxShape.circle,
                  ),
                  child: Icon(
                    Icons.close,
                    size: 16,
                    color: Colors.white,
                  ),
                ),
              ),
            ),
          ],
        )),
        if (controller.images.length < 9)
          Container(
            width: 100,
            height: 100,
            decoration: BoxDecoration(
              color: Colors.grey[200],
              borderRadius: BorderRadius.circular(8),
            ),
            child: IconButton(
              icon: Icon(Icons.add_photo_alternate),
              onPressed: controller.pickImage,
            ),
          ),
      ],
    );
  }
} 