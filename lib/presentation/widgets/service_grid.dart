import 'package:flutter/material.dart';
import '../pages/voice_interaction_page.dart';

class ServiceGrid extends StatelessWidget {
  const ServiceGrid({super.key});

  @override
  Widget build(BuildContext context) {
    return GridView.count(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisCount: 4,
      mainAxisSpacing: 16,
      crossAxisSpacing: 16,
      children: [
        _buildServiceItem(
          context,
          icon: Icons.mic,
          label: '语音助手',
          onTap: () => Navigator.push(
            context,
            MaterialPageRoute(builder: (context) => const VoiceInteractionPage()),
          ),
        ),
        _buildServiceItem(
          context,
          icon: Icons.health_and_safety,
          label: '健康',
          onTap: () {},
        ),
        _buildServiceItem(
          context,
          icon: Icons.medical_services,
          label: '医疗',
          onTap: () {},
        ),
        _buildServiceItem(
          context,
          icon: Icons.local_hospital,
          label: '问诊',
          onTap: () {},
        ),
        _buildServiceItem(
          context,
          icon: Icons.medication,
          label: '用药',
          onTap: () {},
        ),
        _buildServiceItem(
          context,
          icon: Icons.calendar_today,
          label: '预约',
          onTap: () {},
        ),
        _buildServiceItem(
          context,
          icon: Icons.article,
          label: '档案',
          onTap: () {},
        ),
        _buildServiceItem(
          context,
          icon: Icons.more_horiz,
          label: '更多',
          onTap: () {},
        ),
      ],
    );
  }

  Widget _buildServiceItem(
    BuildContext context, {
    required IconData icon,
    required String label,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        decoration: BoxDecoration(
          color: Theme.of(context).colorScheme.surfaceVariant.withOpacity(0.5),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              icon,
              size: 28,
              color: Theme.of(context).colorScheme.primary,
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ],
        ),
      ),
    );
  }
} 