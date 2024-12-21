import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:suoke_life/presentation/controllers/feedback_controller.dart';
import 'package:suoke_life/app/core/widgets/custom_text_field.dart';
import 'package:suoke_life/app/core/widgets/loading_button.dart';
import 'package:suoke_life/routes/app_routes.dart';

class FeedbackPage extends GetView<FeedbackController> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('意见反馈'),
        actions: [
          TextButton(
            onPressed: () => Get.toNamed(AppRoutes.FEEDBACK_HISTORY),
            child: Text('历史记录'),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '请描述您遇到的问题或建议',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w500,
              ),
            ),
            SizedBox(height: 24),

            // 反馈类型
            _buildSectionTitle('反馈类型'),
            _buildTypeSelector(),
            SizedBox(height: 24),

            // 反馈内容
            _buildSectionTitle('反馈内容'),
            CustomTextField(
              controller: controller.contentController,
              hint: '请详细描述您的问题或建议...',
              maxLines: 5,
              maxLength: 500,
            ),
            SizedBox(height: 24),

            // 图片上传
            _buildSectionTitle('图片附件（可选）'),
            _buildImageUploader(),
            SizedBox(height: 24),

            // 联系方式
            _buildSectionTitle('联系方式（可选）'),
            CustomTextField(
              controller: controller.contactController,
              hint: '请留下您的联系方式，方便我们及时反馈',
              maxLength: 50,
            ),
            
            SizedBox(height: 32),
            
            // 提交按钮
            Obx(() => LoadingButton(
              onPressed: controller.submitFeedback,
              isLoading: controller.isSubmitting.value,
              child: Text('提交反馈'),
              width: double.infinity,
            )),
          ],
        ),
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Padding(
      padding: EdgeInsets.only(bottom: 8),
      child: Text(
        title,
        style: TextStyle(
          fontSize: 16,
          fontWeight: FontWeight.bold,
          color: Colors.grey[800],
        ),
      ),
    );
  }

  Widget _buildTypeSelector() {
    return Obx(() => Wrap(
      spacing: 8,
      runSpacing: 8,
      children: controller.feedbackTypes.map((type) {
        final isSelected = controller.selectedType.value == type;
        return ChoiceChip(
          label: Text(type),
          selected: isSelected,
          onSelected: (selected) {
            if (selected) {
              controller.selectedType.value = type;
            }
          },
          selectedColor: Get.theme.primaryColor,
          labelStyle: TextStyle(
            color: isSelected ? Colors.white : Colors.black87,
          ),
        );
      }).toList(),
    ));
  }

  Widget _buildImageUploader() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Obx(() => Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [
            ...controller.images.map((image) => _buildImagePreview(image)),
            if (controller.images.length < 3)
              _buildAddImageButton(),
          ],
        )),
        SizedBox(height: 8),
        Text(
          '最多可上传3张图片',
          style: TextStyle(
            color: Colors.grey[600],
            fontSize: 12,
          ),
        ),
      ],
    );
  }

  Widget _buildImagePreview(image) {
    return Stack(
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
        width: 100,
        height: 100,
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