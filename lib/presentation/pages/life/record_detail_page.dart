import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:suoke_life/presentation/controllers/record_detail_controller.dart';

class RecordDetailPage extends GetView<RecordDetailController> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('记录详情'),
        actions: [
          IconButton(
            icon: Icon(Icons.share),
            onPressed: controller.shareRecord,
          ),
          IconButton(
            icon: Icon(Icons.delete),
            onPressed: controller.deleteRecord,
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 时间
            Text(
              controller.record.time,
              style: TextStyle(
                color: Colors.grey,
                fontSize: 14,
              ),
            ),
            SizedBox(height: 16),
            
            // 内容
            Text(
              controller.record.content,
              style: TextStyle(
                fontSize: 16,
                height: 1.5,
              ),
            ),
            SizedBox(height: 16),
            
            // 图片
            if (controller.record.image != null) ...[
              ClipRRect(
                borderRadius: BorderRadius.circular(8),
                child: Image.asset(
                  controller.record.image!,
                  width: double.infinity,
                  fit: BoxFit.cover,
                ),
              ),
              SizedBox(height: 16),
            ],
            
            // 标签
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: controller.record.tags.map((tag) => Chip(
                label: Text(tag),
                backgroundColor: Colors.grey.shade100,
              )).toList(),
            ),
            
            SizedBox(height: 32),
            
            // AI分析按钮
            Center(
              child: ElevatedButton.icon(
                onPressed: controller.analyzeWithAI,
                icon: Icon(Icons.psychology),
                label: Text('AI分析'),
                style: ElevatedButton.styleFrom(
                  padding: EdgeInsets.symmetric(horizontal: 32, vertical: 16),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
} 