import 'package:get/get.dart';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';

class FeedbackService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();

  final feedbacks = <Map<String, dynamic>>[].obs;
  final categories = <String>[].obs;
  final isProcessing = false.obs;

  @override
  void onInit() {
    super.onInit();
    _initFeedback();
  }

  Future<void> _initFeedback() async {
    try {
      await _loadFeedbacks();
      await _loadCategories();
    } catch (e) {
      await _loggingService.log('error', 'Failed to initialize feedback', data: {'error': e.toString()});
    }
  }

  // 提交反馈
  Future<void> submitFeedback({
    required String userId,
    required String category,
    required String content,
    Map<String, dynamic>? metadata,
    List<String>? attachments,
  }) async {
    if (isProcessing.value) return;

    try {
      isProcessing.value = true;

      final feedback = {
        'user_id': userId,
        'category': category,
        'content': content,
        'metadata': metadata,
        'attachments': attachments,
        'status': 'pending',
        'timestamp': DateTime.now().toIso8601String(),
      };

      await _validateFeedback(feedback);
      await _saveFeedback(feedback);
      await _processFeedback(feedback);
    } catch (e) {
      await _loggingService.log('error', 'Failed to submit feedback', data: {'error': e.toString()});
      rethrow;
    } finally {
      isProcessing.value = false;
    }
  }

  // 更新反馈状态
  Future<void> updateFeedbackStatus(String feedbackId, String status) async {
    try {
      final index = feedbacks.indexWhere((f) => f['id'] == feedbackId);
      if (index == -1) {
        throw Exception('Feedback not found');
      }

      feedbacks[index] = {
        ...feedbacks[index],
        'status': status,
        'updated_at': DateTime.now().toIso8601String(),
      };

      await _saveFeedbacks();
    } catch (e) {
      await _loggingService.log('error', 'Failed to update feedback status', data: {'error': e.toString()});
      rethrow;
    }
  }

  // 获取反馈统计
  Future<Map<String, dynamic>> getFeedbackStats() async {
    try {
      return {
        'total_feedbacks': feedbacks.length,
        'category_distribution': _calculateCategoryDistribution(),
        'status_distribution': _calculateStatusDistribution(),
        'recent_feedbacks': _getRecentFeedbacks(10),
        'trends': await _analyzeFeedbackTrends(),
      };
    } catch (e) {
      await _loggingService.log('error', 'Failed to get feedback stats', data: {'error': e.toString()});
      return {};
    }
  }

  Future<void> _loadFeedbacks() async {
    try {
      final saved = await _storageService.getLocal('feedbacks');
      if (saved != null) {
        feedbacks.value = List<Map<String, dynamic>>.from(saved);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _loadCategories() async {
    try {
      final saved = await _storageService.getLocal('feedback_categories');
      if (saved != null) {
        categories.value = List<String>.from(saved);
      } else {
        // 默认分类
        categories.value = [
          'bug_report',
          'feature_request',
          'performance_issue',
          'usability_feedback',
          'other',
        ];
        await _storageService.saveLocal('feedback_categories', categories);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _validateFeedback(Map<String, dynamic> feedback) async {
    if (!categories.contains(feedback['category'])) {
      throw Exception('Invalid feedback category');
    }

    if (feedback['content'].toString().trim().isEmpty) {
      throw Exception('Feedback content cannot be empty');
    }
  }

  Future<void> _saveFeedback(Map<String, dynamic> feedback) async {
    try {
      feedbacks.insert(0, feedback);
      await _saveFeedbacks();
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveFeedbacks() async {
    try {
      await _storageService.saveLocal('feedbacks', feedbacks);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _processFeedback(Map<String, dynamic> feedback) async {
    try {
      await _analyzeSentiment(feedback);
      await _categorize(feedback);
      await _prioritize(feedback);
      await _notifyRelevantTeams(feedback);
    } catch (e) {
      rethrow;
    }
  }

  Map<String, int> _calculateCategoryDistribution() {
    final distribution = <String, int>{};
    for (final feedback in feedbacks) {
      final category = feedback['category'];
      distribution[category] = (distribution[category] ?? 0) + 1;
    }
    return distribution;
  }

  Map<String, int> _calculateStatusDistribution() {
    final distribution = <String, int>{};
    for (final feedback in feedbacks) {
      final status = feedback['status'];
      distribution[status] = (distribution[status] ?? 0) + 1;
    }
    return distribution;
  }

  List<Map<String, dynamic>> _getRecentFeedbacks(int count) {
    return feedbacks.take(count).toList();
  }

  Future<Map<String, dynamic>> _analyzeFeedbackTrends() async {
    try {
      final trends = <String, dynamic>{};
      
      // 按月分组
      final monthlyFeedbacks = <String, List<Map<String, dynamic>>>{};
      for (final feedback in feedbacks) {
        final date = DateTime.parse(feedback['timestamp']);
        final month = '${date.year}-${date.month.toString().padLeft(2, '0')}';
        monthlyFeedbacks[month] = monthlyFeedbacks[month] ?? [];
        monthlyFeedbacks[month]!.add(feedback);
      }

      // 计算每月统计
      for (final entry in monthlyFeedbacks.entries) {
        trends[entry.key] = {
          'count': entry.value.length,
          'categories': _calculateCategoryDistribution(),
          'statuses': _calculateStatusDistribution(),
        };
      }

      return trends;
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _analyzeSentiment(Map<String, dynamic> feedback) async {
    try {
      // TODO: 实现情感分析
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _categorize(Map<String, dynamic> feedback) async {
    try {
      // TODO: 实现自动分类
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _prioritize(Map<String, dynamic> feedback) async {
    try {
      // TODO: 实现优先级评估
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _notifyRelevantTeams(Map<String, dynamic> feedback) async {
    try {
      // TODO: 实现团队通知
    } catch (e) {
      rethrow;
    }
  }
} 