import 'dart:convert';
import 'package:get/get.dart';
import '../core/database/database_helper.dart';
import '../data/models/feedback.dart';

class FeedbackService extends GetxService {
  final _db = DatabaseHelper.instance;

  Future<List<FeedbackRecord>> getFeedbacks() async {
    final results = await _db.queryAll('feedback_records');
    return results.map((map) => FeedbackRecord.fromJson(map)).toList();
  }

  Future<void> saveFeedback(FeedbackRecord feedback) async {
    await _db.insert('feedback_records', feedback.toJson());
  }

  Future<void> updateFeedback(FeedbackRecord feedback) async {
    await _db.update('feedback_records', feedback.toJson(), feedback.id);
  }
} 