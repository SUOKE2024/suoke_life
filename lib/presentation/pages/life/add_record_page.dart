import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:suoke_life/presentation/controllers/add_record_controller.dart';
import 'package:suoke_life/app/core/widgets/custom_text_field.dart';
import 'package:suoke_life/app/core/widgets/loading_button.dart';

class AddRecordPage extends GetView<AddRecordController> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('添加记录'),
      ),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 标题输入
            CustomTextField(
              label: '标题',
              hint: '请输入标题',
              controller: controller.titleController,
              maxLength: 50,
            ),
            SizedBox(height: 16),

            // 内容输入
            CustomTextField(
              label: '内容',
              hint: '请输入内容',
              controller: controller.contentController,
              maxLines: 5,
              maxLength: 500,
            ),
            SizedBox(height: 16),

            // 标签选择
            _buildTagSelector(),
            SizedBox(height: 16),

            // 图片上传
            _buildImageUploader(),
            SizedBox(height: 24),

            // 提交按钮
            Obx(() => LoadingButton(
              onPressed: controller.submitRecord,
              isLoading: controller.isSubmitting.value,
              child: Text('保存'),
              width: double.infinity,
            )),
          ],
        ),
      ),
    );
  }

  Widget _buildTagSelector() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '标签',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w500,
          ),
        ),
        SizedBox(height: 8),
        Obx(() => Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [
            ...controller.selectedTags.map((tag) => Chip(
              label: Text(tag),
              onDeleted: () => controller.removeTag(tag),
            )),
            ActionChip(
              label: Text('添加标签'),
              onPressed: controller.showTagSelector,
            ),
          ],
        )),
      ],
    );
  }

  Widget _buildImageUploader() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '图片',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w500,
          ),
        ),
        SizedBox(height: 8),
        Obx(() => Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [
            ...controller.images.map((image) => _buildImagePreview(image)),
            if (controller.images.length < 9)
              _buildAddImageButton(),
          ],
        )),
      ],
    );
  }

  Widget _buildImagePreview(image) {
    return Stack(
      children: [
        Container(
          width: 80,
          height: 80,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(8),
            image: DecorationImage(
              image: FileImage(image),
              fit: BoxFit.cover,
            ),
          ),
        ),
        Positioned(
          top: 4,
          right: 4,
          child: GestureDetector(
            onTap: () => controller.removeImage(image),
            child: Container(
              padding: EdgeInsets.all(4),
              decoration: BoxDecoration(
                color: Colors.black54,
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
    );
  }

  Widget _buildAddImageButton() {
    return InkWell(
      onTap: controller.pickImage,
      child: Container(
        width: 80,
        height: 80,
        decoration: BoxDecoration(
          color: Colors.grey[200],
          borderRadius: BorderRadius.circular(8),
        ),
        child: Icon(
          Icons.add_photo_alternate,
          color: Colors.grey[400],
          size: 32,
        ),
      ),
    );
  }
} 