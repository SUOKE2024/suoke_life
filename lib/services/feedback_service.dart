import 'package:get/get.dart';
import 'package:hive/hive.dart';
import 'package:suoke_life/data/models/feedback.dart';

class FeedbackService extends GetxService {
  late Box<FeedbackRecord> _feedbackBox;
  
  // 初始化
  Future<void> init() async {
    _feedbackBox = await Hive.openBox<FeedbackRecord>('feedback');
  }
  
  // 提交反馈
  Future<void> submitFeedback(FeedbackRecord feedback) async {
    await _feedbackBox.add(feedback);
  }
  
  // 获取反馈历史
  List<FeedbackRecord> getFeedbackHistory() {
    return _feedbackBox.values.toList()
      ..sort((a, b) => b.time.compareTo(a.time));
  }
  
  // 更新反馈状态
  Future<void> updateFeedbackStatus(String id, String status) async {
    final index = _feedbackBox.values.toList()
      .indexWhere((feedback) => feedback.id == id);
    if (index != -1) {
      final feedback = _feedbackBox.getAt(index);
      if (feedback != null) {
        final updatedFeedback = FeedbackRecord(
          id: feedback.id,
          type: feedback.type,
          content: feedback.content,
          contact: feedback.contact,
          images: feedback.images,
          time: feedback.time,
          status: status,
        );
        await _feedbackBox.putAt(index, updatedFeedback);
      }
    }
  }
  
  // 删除反馈
  Future<void> deleteFeedback(String id) async {
    final index = _feedbackBox.values.toList()
      .indexWhere((feedback) => feedback.id == id);
    if (index != -1) {
      await _feedbackBox.deleteAt(index);
    }
  }
  
  // 清空反馈历史
  Future<void> clearFeedbackHistory() async {
    await _feedbackBox.clear();
  }
} 