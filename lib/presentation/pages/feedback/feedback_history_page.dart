import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:suoke_life/presentation/controllers/feedback_controller.dart';
import 'package:suoke_life/app/core/widgets/empty_placeholder.dart';

class FeedbackHistoryPage extends GetView<FeedbackController> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('反馈历史'),
      ),
      body: Obx(() {
        if (controller.feedbackHistory.isEmpty) {
          return EmptyPlaceholder(
            message: '暂无反馈记录',
            action: TextButton(
              onPressed: () => Get.back(),
              child: Text('去提交反馈'),
            ),
          );
        }

        return RefreshIndicator(
          onRefresh: controller.refreshFeedbackHistory,
          child: ListView.builder(
            padding: EdgeInsets.all(16),
            itemCount: controller.feedbackHistory.length,
            itemBuilder: (context, index) {
              final feedback = controller.feedbackHistory[index];
              return _buildFeedbackCard(feedback);
            },
          ),
        );
      }),
    );
  }

  Widget _buildFeedbackCard(feedback) {
    return Card(
      margin: EdgeInsets.only(bottom: 16),
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 2,
                  ),
                  decoration: BoxDecoration(
                    color: Get.theme.primaryColor.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    feedback.type,
                    style: TextStyle(
                      color: Get.theme.primaryColor,
                      fontSize: 12,
                    ),
                  ),
                ),
                Spacer(),
                Text(
                  _formatTime(feedback.time),
                  style: TextStyle(
                    color: Colors.grey[600],
                    fontSize: 12,
                  ),
                ),
              ],
            ),
            SizedBox(height: 12),
            Text(
              feedback.content,
              style: TextStyle(
                fontSize: 14,
                height: 1.5,
              ),
            ),
            if (feedback.images.isNotEmpty) ...[
              SizedBox(height: 12),
              _buildImageList(feedback.images),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildImageList(List<String> images) {
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: images.map((url) => Container(
        width: 80,
        height: 80,
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(4),
          image: DecorationImage(
            image: NetworkImage(url),
            fit: BoxFit.cover,
          ),
        ),
      )).toList(),
    );
  }

  String _formatTime(String time) {
    final date = DateTime.parse(time);
    final now = DateTime.now();
    final diff = now.difference(date);

    if (diff.inMinutes < 1) {
      return '刚刚';
    } else if (diff.inHours < 1) {
      return '${diff.inMinutes}分钟前';
    } else if (diff.inDays < 1) {
      return '${diff.inHours}小时前';
    } else if (diff.inDays < 30) {
      return '${diff.inDays}天前';
    } else {
      return '${date.year}-${date.month}-${date.day}';
    }
  }
} 