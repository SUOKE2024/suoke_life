import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/core/constants/app_colors.dart';
import 'package:suoke_life/core/router/app_router.dart';
import 'package:suoke_life/core/router/tcm_routes.dart';
import 'package:suoke_life/core/widgets/animated_gradient_card.dart';

@RoutePage()
class TcmFeaturesPage extends ConsumerWidget {
  const TcmFeaturesPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('中医特色功能'),
        backgroundColor: AppColors.SUOKE_GREEN,
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                '四诊合参',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 16),
              _buildDiagnosticFeatureCard(
                context,
                title: '多模态智能诊断',
                description: '结合舌诊、面诊、声音分析和症状描述，进行智能辨证分析',
                icon: Icons.health_and_safety,
                colors: [
                  const Color(0xFF35BB78),
                  const Color(0xFF2DA160),
                  const Color(0xFF35BB78),
                ],
                onTap: () => context.router.pushNamed(TcmRoutes.multimodalDiagnosisPath),
              ),
              const SizedBox(height: 16),
              _buildDiagnosticFeatureCard(
                context,
                title: '舌诊分析',
                description: '通过舌象分析体质特征和健康状态',
                icon: Icons.spa,
                colors: [
                  const Color(0xFF4C8DAE),
                  const Color(0xFF3A7A9C),
                  const Color(0xFF4C8DAE),
                ],
                onTap: () => context.router.pushNamed(TcmRoutes.tongueDiagnosisPath),
              ),
              const SizedBox(height: 16),
              _buildDiagnosticFeatureCard(
                context,
                title: '脉诊分析',
                description: '通过脉象分析体内气血状态和脏腑功能',
                icon: Icons.favorite,
                colors: [
                  const Color(0xFFFF6800),
                  const Color(0xFFE25A00),
                  const Color(0xFFFF6800),
                ],
                onTap: () => context.router.pushNamed(TcmRoutes.pulseDiagnosisPath),
              ),
              const SizedBox(height: 24),
              const Text(
                '体质辨识',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 16),
              _buildFeatureCard(
                context,
                title: '体质测评',
                description: '分析九种体质类型，提供个性化健康建议',
                icon: Icons.person,
                colors: [
                  const Color(0xFF9370DB),
                  const Color(0xFF8A2BE2),
                  const Color(0xFF9370DB),
                ],
                onTap: () => {},
              ),
              const SizedBox(height: 24),
              const Text(
                '食疗调理',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 16),
              _buildFeatureCard(
                context,
                title: '体质食疗',
                description: '根据不同体质提供个性化食疗方案',
                icon: Icons.restaurant,
                colors: [
                  const Color(0xFF1E90FF),
                  const Color(0xFF4169E1),
                  const Color(0xFF1E90FF),
                ],
                onTap: () => {},
              ),
              const SizedBox(height: 16),
              _buildFeatureCard(
                context,
                title: '时令养生',
                description: '基于二十四节气的时令养生食谱推荐',
                icon: Icons.wb_sunny,
                colors: [
                  const Color(0xFFFF8C00),
                  const Color(0xFFFF7F50),
                  const Color(0xFFFF8C00),
                ],
                onTap: () => {},
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDiagnosticFeatureCard(
    BuildContext context, {
    required String title,
    required String description,
    required IconData icon,
    required List<Color> colors,
    required VoidCallback onTap,
  }) {
    return AnimatedGradientCard(
      onTap: onTap,
      colors: colors,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.white.withAlpha(70),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(
                    icon,
                    color: Colors.white,
                    size: 24,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    title,
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                ),
                const Icon(
                  Icons.arrow_forward_ios,
                  color: Colors.white,
                  size: 16,
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              description,
              style: const TextStyle(
                fontSize: 14,
                color: Colors.white,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFeatureCard(
    BuildContext context, {
    required String title,
    required String description,
    required IconData icon,
    required List<Color> colors,
    required VoidCallback onTap,
  }) {
    return AnimatedGradientCard(
      onTap: onTap,
      colors: colors,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.white.withAlpha(70),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(
                icon,
                color: Colors.white,
                size: 28,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    description,
                    style: const TextStyle(
                      fontSize: 12,
                      color: Colors.white,
                    ),
                  ),
                ],
              ),
            ),
            const Icon(
              Icons.arrow_forward_ios,
              color: Colors.white,
              size: 16,
            ),
          ],
        ),
      ),
    );
  }
}