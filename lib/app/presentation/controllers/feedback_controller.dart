import 'dart:io';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:image_picker/image_picker.dart';
import '../../data/models/feedback_record.dart';

class FeedbackController extends GetxController {
  final isSubmitting = false.obs;
  final selectedImages = <File>[].obs;
  final feedbackType = 'bug'.obs;
  final contentController = TextEditingController();
  final contactController = TextEditingController();

  @override
  void onClose() {
    contentController.dispose();
    contactController.dispose();
    super.onClose();
  }

  Future<void> pickImage() async {
    try {
      final image = await ImagePicker().pickImage(source: ImageSource.gallery);
      if (image != null) {
        selectedImages.add(File(image.path));
      }
    } catch (e) {
      debugPrint('选择图片失败: $e');
    }
  }

  void removeImage(int index) {
    selectedImages.removeAt(index);
  }

  Future<void> submit() async {
    if (contentController.text.isEmpty) {
      Get.snackbar('提示', '请输入反馈内容');
      return;
    }

    try {
      isSubmitting.value = true;
      
      // TODO: 实现提交逻辑
      await Future.delayed(const Duration(seconds: 1));
      
      Get.back();
      Get.snackbar('提示', '反馈提交成功');
    } catch (e) {
      Get.snackbar('错误', '提交失败，请重试');
      debugPrint('提交反馈失败: $e');
    } finally {
      isSubmitting.value = false;
    }
  }
} 