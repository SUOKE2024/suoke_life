import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../data/models/feedback_record.dart';

class FeedbackHistoryController extends GetxController {
  final isLoading = true.obs;
  final feedbackRecords = <FeedbackRecord>[].obs;

  @override
  void onInit() {
    super.onInit();
    _loadFeedbackHistory();
  }

  Future<void> _loadFeedbackHistory() async {
    try {
      isLoading.value = true;
      
      // TODO: 从服务器加载反馈历史
      await Future.delayed(const Duration(seconds: 1));
      
      // 模拟数据
      feedbackRecords.value = [
        FeedbackRecord(
          id: '1',
          type: 'bug',
          content: '应用闪退问题',
          createdAt: DateTime.now().subtract(const Duration(days: 1)),
          reply: '感谢反馈，我们会尽快修复',
        ),
        FeedbackRecord(
          id: '2',
          type: 'suggestion',
          content: '建议添加深色模式',
          createdAt: DateTime.now().subtract(const Duration(days: 3)),
        ),
      ];
    } catch (e) {
      debugPrint('加载反馈历史失败: $e');
    } finally {
      isLoading.value = false;
    }
  }

  Future<void> refreshData() => _loadFeedbackHistory();
} 