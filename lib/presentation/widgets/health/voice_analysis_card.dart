import 'package:flutter/material.dart';

class VoiceAnalysisCard extends StatelessWidget {
  final Map<String, dynamic> voiceAnalysis;

  const VoiceAnalysisCard({
    Key? key,
    required this.voiceAnalysis,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.mic, color: Colors.blue),
                const SizedBox(width: 8),
                Text(
                  '语音分析',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
              ],
            ),
            const SizedBox(height: 16),
            
            // 语音特征
            _buildSection(
              context,
              '语音特征',
              voiceAnalysis['voiceFeatures'] as Map<String, dynamic>,
            ),
            const Divider(),
            
            // 情绪状态
            _buildSection(
              context,
              '情绪状态',
              voiceAnalysis['emotionalState'] as Map<String, dynamic>,
            ),
            const Divider(),
            
            // 健康评估
            _buildSection(
              context,
              '健康评估',
              voiceAnalysis['healthAssessment'] as Map<String, dynamic>,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSection(
    BuildContext context,
    String title,
    Map<String, dynamic> data,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: Theme.of(context).textTheme.titleMedium,
        ),
        const SizedBox(height: 8),
        ...data.entries.map((entry) => Padding(
          padding: const EdgeInsets.symmetric(vertical: 4),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                entry.key,
                style: Theme.of(context).textTheme.bodyLarge,
              ),
              _buildValueWidget(context, entry.value),
            ],
          ),
        )),
      ],
    );
  }

  Widget _buildValueWidget(BuildContext context, dynamic value) {
    if (value is num) {
      return Text(
        value.toStringAsFixed(2),
        style: TextStyle(
          color: _getValueColor(value),
          fontWeight: FontWeight.bold,
        ),
      );
    } else if (value is String) {
      return Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        decoration: BoxDecoration(
          color: _getStatusColor(value).withOpacity(0.1),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Text(
          value,
          style: TextStyle(
            color: _getStatusColor(value),
            fontWeight: FontWeight.bold,
          ),
        ),
      );
    }
    return Text(value.toString());
  }

  Color _getValueColor(num value) {
    if (value < 0.3) return Colors.red;
    if (value < 0.7) return Colors.orange;
    return Colors.green;
  }

  Color _getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'normal':
      case 'positive':
      case 'good':
        return Colors.green;
      case 'warning':
      case 'neutral':
      case 'moderate':
        return Colors.orange;
      case 'danger':
      case 'negative':
      case 'poor':
        return Colors.red;
      default:
        return Colors.blue;
    }
  }
} 