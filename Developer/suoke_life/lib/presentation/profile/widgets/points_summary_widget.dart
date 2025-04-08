import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:auto_route/auto_route.dart';
import '../../../core/router/app_router.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/widgets/animated_gradient_card.dart';
import '../../../core/widgets/animated_press_button.dart';
import '../../../di/providers/user_providers.dart';

class PointsSummaryWidget extends ConsumerWidget {
  const PointsSummaryWidget({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final pointsBalance = ref.watch(pointsBalanceProvider);
    final vouchersCount = ref.watch(vouchersCountProvider);
    
    return AnimatedGradientCard(
      title: '我的积分',
      subtitle: '查看您的积分与兑换券',
      gradientColors: [AppColors.secondaryColor, AppColors.secondaryDarkColor],
      child: pointsBalance.when(
        data: (balance) => Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: _buildPointsItem(
                    context,
                    title: '索克积分',
                    value: balance.sokelifePoints,
                    iconData: Icons.stars_rounded,
                    color: AppColors.primaryColor,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: _buildPointsItem(
                    context,
                    title: '索克币',
                    value: balance.sokelifeCoins,
                    iconData: Icons.token_rounded,
                    color: AppColors.secondaryColor,
                  ),
                ),
              ],
            ),
            
            const SizedBox(height: 16),
            
            vouchersCount.when(
              data: (count) => _buildVoucherSection(context, count),
              loading: () => _buildVoucherSection(context, null),
              error: (_, __) => _buildVoucherSection(context, 0),
            ),
            
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: AnimatedPressButton(
                    onPressed: () => context.router.push(const PointsHistoryRoute()),
                    child: const Text('积分明细'),
                    backgroundColor: Colors.white,
                    textColor: AppColors.secondaryColor,
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: AnimatedPressButton(
                    onPressed: () => context.router.push(const AchievementsRoute()),
                    child: const Text('成就徽章'),
                    backgroundColor: AppColors.primaryColor,
                    textColor: Colors.white,
                  ),
                ),
              ],
            ),
          ],
        ),
        loading: () => const Center(
          child: CircularProgressIndicator(
            valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
          ),
        ),
        error: (_, __) => Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Text(
              '无法加载积分信息',
              style: TextStyle(color: Colors.white),
            ),
            const SizedBox(height: 12),
            AnimatedPressButton(
              onPressed: () => ref.refresh(pointsBalanceProvider),
              child: const Text('重试'),
              backgroundColor: Colors.white,
              textColor: AppColors.secondaryColor,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPointsItem(
    BuildContext context, {
    required String title,
    required int value,
    required IconData iconData,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white.withAlpha(40),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                iconData,
                color: Colors.white,
                size: 20,
              ),
              const SizedBox(width: 6),
              Text(
                title,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 14,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            value.toString(),
            style: const TextStyle(
              color: Colors.white,
              fontSize: 24,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildVoucherSection(BuildContext context, int? count) {
    return GestureDetector(
      onTap: () => context.router.push(const VouchersRoute()),
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Colors.white.withAlpha(40),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Row(
          children: [
            const Icon(
              Icons.card_giftcard,
              color: Colors.white,
              size: 24,
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    '服务券',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    count == null ? '加载中...' : '您有 $count 张未使用的服务券',
                    style: TextStyle(
                      color: Colors.white.withAlpha(200),
                      fontSize: 14,
                    ),
                  ),
                ],
              ),
            ),
            const Icon(
              Icons.chevron_right,
              color: Colors.white,
              size: 24,
            ),
          ],
        ),
      ),
    );
  }
}