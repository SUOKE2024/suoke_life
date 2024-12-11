import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import '../models/topic.dart';

class TopicHeader extends StatelessWidget {
  final Topic topic;

  const TopicHeader({
    super.key,
    required this.topic,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.all(16.w),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                topic.icon,
                size: 32.w,
                color: topic.color,
              ),
              SizedBox(width: 8.w),
              Text(
                topic.name,
                style: TextStyle(
                  fontSize: 24.sp,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          if (topic.description != null) ...[
            SizedBox(height: 8.h),
            Text(
              topic.description!,
              style: TextStyle(
                fontSize: 14.sp,
                color: Colors.grey[600],
              ),
            ),
          ],
          SizedBox(height: 16.h),
          Wrap(
            spacing: 8.w,
            runSpacing: 8.h,
            children: topic.tags.map((tag) => Chip(
              label: Text(tag),
              backgroundColor: topic.color.withOpacity(0.1),
              labelStyle: TextStyle(
                color: topic.color,
              ),
            )).toList(),
          ),
        ],
      ),
    );
  }
} 