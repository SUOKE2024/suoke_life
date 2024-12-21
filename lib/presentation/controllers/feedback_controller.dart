import 'package:get/get.dart';
import 'package:flutter/material.dart';
import 'dart:io';
import 'package:suoke_life/services/feedback_service.dart';
import 'package:suoke_life/data/models/feedback_record.dart';

class FeedbackController extends GetxController {
  final FeedbackService _feedbackService = Get.find();
  
  // 文本控制器
  final contentController = TextEditingController();
  final contactController = TextEditingController();
  
  // 反馈类型
  final feedbackTypes = ['功能建议', '问题反馈', '其他'].obs;
  final selectedType = '功能建议'.obs;
  
  // 图片列表
  final images = <File>[].obs;
  
  // 提交状态
  final isSubmitting = false.obs;

  // 反馈历史
  final _feedbackHistory = <FeedbackRecord>[].obs;
  List<FeedbackRecord> get feedbackHistory => _feedbackHistory;
  
  @override
  void onInit() {
    super.onInit();
    loadFeedbackHistory();
  }

  // 加载反馈历史
  Future<void> loadFeedbackHistory() async {
    try {
      final history = await _feedbackService.getFeedbackHistory();
      _feedbackHistory.value = history;
    } catch (e) {
      Get.snackbar('错误', '加载反馈历史失败: $e');
    }
  }

  // 刷新反馈历史
  Future<void> refreshFeedbackHistory() async {
    await loadFeedbackHistory();
  }
  
  @override
  void onClose() {
    contentController.dispose();
    contactController.dispose();
    super.onClose();
  }
  
  // 选择图片
  Future<void> pickImage() async {
    try {
      // TODO: 实现图片选择
    } catch (e) {
      Get.snackbar('错误', '选择图片失败: $e');
    }
  }
  
  // 移除图片
  void removeImage(File image) {
    images.remove(image);
  }
  
  // 提交反馈
  Future<void> submitFeedback() async {
    if (contentController.text.isEmpty) {
      Get.snackbar('提示', '请输入反馈内容');
      return;
    }
    
    try {
      isSubmitting.value = true;
      
      final feedback = {
        'type': selectedType.value,
        'content': contentController.text,
        'contact': contactController.text,
        'images': images,
      };
      
      await _feedbackService.submitFeedback(feedback);
      
      Get.back();
      Get.snackbar('成功', '感谢您的反馈');
      
    } catch (e) {
      Get.snackbar('错误', '提交反馈失败: $e');
    } finally {
      isSubmitting.value = false;
    }
  }
} 