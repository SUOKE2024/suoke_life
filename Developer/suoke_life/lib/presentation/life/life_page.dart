import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:auto_route/auto_route.dart';
import 'package:suoke_life/core/router/app_router.dart';
import 'package:suoke_life/core/theme/app_colors.dart';
import 'package:suoke_life/presentation/common/widgets/custom_app_bar.dart';

@RoutePage()
class LifePage extends ConsumerWidget {
  const LifePage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: CustomAppBar(
        title: const Text('LIFE'),
        centerTitle: true,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildDailyHealthCard(context),
              const SizedBox(height: 24),
              Text(
                '健康服务',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: 16),
              _buildFeatureCards(context),
              const SizedBox(height: 24),
              Text(
                '养生小助手',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: 16),
              _buildHealthTipsCard(context),
            ],
          ),
        ),
      ),
    );
  }

  // 每日健康卡片
  Widget _buildDailyHealthCard(BuildContext context) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.calendar_today, color: AppColors.brandPrimary),
                const SizedBox(width: 8),
                Text(
                  '今日健康',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                const Spacer(),
                TextButton(
                  onPressed: () {
                    context.router.push(const HealthProfileRoute());
                  },
                  child: const Text('查看健康画像'),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildDailyHealthIndicator(
                  context,
                  '睡眠',
                  '7.5小时',
                  Icons.nightlight_round,
                ),
                _buildDailyHealthIndicator(
                  context,
                  '步数',
                  '8,730',
                  Icons.directions_walk,
                ),
                _buildDailyHealthIndicator(
                  context,
                  '心率',
                  '72 bpm',
                  Icons.favorite,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  // 每日健康指标
  Widget _buildDailyHealthIndicator(
      BuildContext context, String title, String value, IconData icon) {
    return Column(
      children: [
        Icon(icon, color: AppColors.brandPrimary),
        const SizedBox(height: 8),
        Text(
          value,
          style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                fontWeight: FontWeight.bold,
              ),
        ),
        const SizedBox(height: 4),
        Text(
          title,
          style: Theme.of(context).textTheme.bodySmall,
        ),
      ],
    );
  }

  // 功能卡片
  Widget _buildFeatureCards(BuildContext context) {
    return GridView.count(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisCount: 2,
      mainAxisSpacing: 16,
      crossAxisSpacing: 16,
      childAspectRatio: 1.2,
      children: [
        // 健康画像卡片
        _buildFeatureCard(
          context: context,
          title: '健康画像',
          icon: Icons.person,
          color: AppColors.brandPrimary,
          onTap: () => context.router.push(const HealthProfileRoute()),
        ),

        // 体质测评
        _buildFeatureCard(
          context: context,
          title: '体质测评',
          icon: Icons.accessibility_new,
          color: AppColors.brandSecondary,
          onTap: () {
            // 体质测评功能
          },
        ),

        // 食疗推荐
        _buildFeatureCard(
          context: context,
          title: '食疗推荐',
          icon: Icons.restaurant,
          color: Colors.green,
          onTap: () {
            // 食疗推荐功能
          },
        ),

        // 经络调理
        _buildFeatureCard(
          context: context,
          title: '经络调理',
          icon: Icons.spa,
          color: Colors.purple,
          onTap: () {
            // 经络调理功能
          },
        ),
      ],
    );
  }

  // 功能卡片
  Widget _buildFeatureCard({
    required BuildContext context,
    required String title,
    required IconData icon,
    required Color color,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Card(
        elevation: 4,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                icon,
                size: 40,
                color: color,
              ),
              const SizedBox(height: 12),
              Text(
                title,
                style: Theme.of(context).textTheme.titleMedium,
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }

  // 养生小贴士卡片
  Widget _buildHealthTipsCard(BuildContext context) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.tips_and_updates,
                    color: AppColors.brandPrimary),
                const SizedBox(width: 8),
                Text(
                  '养生小贴士',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
              ],
            ),
            const SizedBox(height: 16),
            const Text(
              '今日节气: 小满 - 夏季的第二个节气',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            const Text(
              '小满养生重点：心经当令，注意心火上炎，保持心情舒畅，多食酸甘化阴之品，如绿豆、荸荠、莲子等。',
            ),
            const SizedBox(height: 16),
            const Text(
              '适宜穴位按摩：内关穴、神门穴',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            const Text(
              '内关穴：位于腕横纹上2寸，两筋之间。按摩可缓解心悸、失眠、胸闷等症状。',
            ),
          ],
        ),
      ),
    );
  }
}
