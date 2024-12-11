import 'package:flutter/material.dart';
import '../../services/consultation_service.dart';
import '../widgets/analysis_card.dart';
import '../widgets/expert_list.dart';
import '../widgets/consultation_info_card.dart';

class ConsultationResultPage extends StatelessWidget {
  final ConsultationResult result;

  const ConsultationResultPage({
    Key? key,
    required this.result,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('会诊安排'),
        actions: [
          IconButton(
            icon: const Icon(Icons.share),
            onPressed: () {
              // TODO: 实现分享功能
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            ConsultationInfoCard(
              consultationId: result.consultationId,
              scheduledTime: result.scheduledTime,
              zoomLink: result.zoomLink,
            ),
            const SizedBox(height: 16),
            AnalysisCard(analysis: result.analysis),
            const SizedBox(height: 16),
            ExpertList(experts: result.matchedExperts),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: () {
                // TODO: 实现加入会议功能
              },
              icon: const Icon(Icons.video_call),
              label: const Text('加入视频会诊'),
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
            ),
            const SizedBox(height: 8),
            TextButton.icon(
              onPressed: () {
                // TODO: 实现重新安排功能
              },
              icon: const Icon(Icons.schedule),
              label: const Text('重新安排时间'),
            ),
          ],
        ),
      ),
    );
  }
} 