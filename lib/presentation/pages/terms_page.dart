import 'package:flutter/material.dart';

class TermsPage extends StatelessWidget {
  final String title;
  final String content;

  const TermsPage({
    super.key,
    required this.title,
    required this.content,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(title),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: const TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              '更新日期：2024年1月1日',
              style: TextStyle(
                color: Colors.grey[600],
                fontSize: 14,
              ),
            ),
            const SizedBox(height: 24),
            Text(
              content,
              style: const TextStyle(
                fontSize: 16,
                height: 1.6,
              ),
            ),
          ],
        ),
      ),
    );
  }
} 