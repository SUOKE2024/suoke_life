import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../core/base/base_page.dart';
import '../../controllers/feedback_controller.dart';

class FeedbackPage extends BasePage<FeedbackController> {
  const FeedbackPage({Key? key}) : super(key: key);

  @override
  PreferredSizeWidget buildAppBar(BuildContext context) {
    return AppBar(
      title: const Text('意见反馈'),
      actions: [
        TextButton(
          onPressed: controller.submitFeedback,
          child: const Text('提交'),
        ),
      ],
    );
  }

  @override
  Widget buildBody(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 反馈类型选择
          Text(
            '反馈类型',
            style: Get.textTheme.titleMedium,
          ),
          const SizedBox(height: 8),
          Obx(() => Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              '功能建议',
              '问题反馈',
              '体验优化',
              '其他',
            ].map((type) => ChoiceChip(
              label: Text(type),
              selected: controller.selectedType.value == type,
              onSelected: (selected) {
                if (selected) {
                  controller.selectedType.value = type;
                }
              },
            )).toList(),
          )),

          const SizedBox(height: 24),

          // 反馈内容
          Text(
            '反馈内容',
            style: Get.textTheme.titleMedium,
          ),
          const SizedBox(height: 8),
          TextField(
            controller: controller.contentController,
            maxLines: 5,
            maxLength: 500,
            decoration: const InputDecoration(
              hintText: '请详细描述您的建议或遇到的问题...',
              border: OutlineInputBorder(),
            ),
          ),

          const SizedBox(height: 24),

          // 联系方式
          Text(
            '联系方式（选填）',
            style: Get.textTheme.titleMedium,
          ),
          const SizedBox(height: 8),
          TextField(
            controller: controller.contactController,
            decoration: const InputDecoration(
              hintText: '请留下您的联系方式，方便我们及时反馈',
              border: OutlineInputBorder(),
            ),
          ),

          const SizedBox(height: 24),

          // 图片上传
          Text(
            '上传截图（选填）',
            style: Get.textTheme.titleMedium,
          ),
          const SizedBox(height: 8),
          Obx(() => Wrap(
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
                        padding: const EdgeInsets.all(4),
                        decoration: const BoxDecoration(
                          color: Colors.black54,
                          shape: BoxShape.circle,
                        ),
                        child: const Icon(
                          Icons.close,
                          size: 16,
                          color: Colors.white,
                        ),
                      ),
                    ),
                  ),
                ],
              )),
              if (controller.images.length < 3)
                GestureDetector(
                  onTap: controller.pickImage,
                  child: Container(
                    width: 100,
                    height: 100,
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.grey[300]!),
                    ),
                    child: const Icon(
                      Icons.add_photo_alternate_outlined,
                      size: 32,
                      color: Colors.grey,
                    ),
                  ),
                ),
            ],
          )),
        ],
      ),
    );
  }
} 