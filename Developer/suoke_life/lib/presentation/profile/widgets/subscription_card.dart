import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:auto_route/auto_route.dart';
import 'package:intl/intl.dart';
import '../../../core/router/app_router.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/widgets/animated_gradient_card.dart';
import '../../../core/widgets/animated_press_button.dart';
import '../../../di/providers/user_providers.dart';
import '../../../domain/entities/subscription.dart';

class SubscriptionCard extends ConsumerWidget {
  const SubscriptionCard({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final userSubscription = ref.watch(userSubscriptionProvider);
    
    return AnimatedGradientCard(
      title: '我的订阅',
      subtitle: '管理您的订阅计划',
      gradientColors: [AppColors.primaryDarkColor, Color(0xFF1A7A4D)],
      child: userSubscription.when(
        data: (subscription) {
          if (subscription == null) {
            return _buildNoSubscription(context);
          }
          
          return Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: Colors.white.withAlpha(40),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    Icon(
                      _getPlanIcon(subscription.planId),
                      color: Colors.white,
                      size: 28,
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Text(
                                subscription.planName,
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontSize: 16,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              const SizedBox(width: 8),
                              _buildStatusBadge(subscription.status),
                            ],
                          ),
                          const SizedBox(height: 4),
                          Text(
                            _getSubscriptionPeriodText(subscription),
                            style: TextStyle(
                              color: Colors.white.withAlpha(220),
                              fontSize: 13,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              
              const SizedBox(height: 16),
              
              if (subscription.isActive && subscription.willAutoRenew)
                _buildRenewalInfo(subscription),
              
              if (subscription.isInGracePeriod)
                _buildGracePeriodWarning(),
                
              const SizedBox(height: 16),
              
              Row(
                children: [
                  Expanded(
                    child: AnimatedPressButton(
                      onPressed: () => context.router.push(const SubscriptionDetailsRoute()),
                      child: const Text('管理订阅'),
                      backgroundColor: Colors.white,
                      textColor: AppColors.primaryColor,
                    ),
                  ),
                  if (subscription.status == SubscriptionStatus.cancelled || 
                      subscription.status == SubscriptionStatus.expired) ...[
                    const SizedBox(width: 8),
                    Expanded(
                      child: AnimatedPressButton(
                        onPressed: () => context.router.push(const SubscriptionPlansRoute()),
                        child: const Text('重新订阅'),
                        backgroundColor: AppColors.secondaryColor,
                        textColor: Colors.white,
                      ),
                    ),
                  ],
                ],
              ),
            ],
          );
        },
        loading: () => const Center(
          child: CircularProgressIndicator(
            valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
          ),
        ),
        error: (_, __) => Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Text(
              '无法加载订阅信息',
              style: TextStyle(color: Colors.white),
            ),
            const SizedBox(height: 12),
            AnimatedPressButton(
              onPressed: () => ref.refresh(userSubscriptionProvider),
              child: const Text('重试'),
              backgroundColor: Colors.white,
              textColor: AppColors.primaryColor,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildNoSubscription(BuildContext context) {
    return Column(
      children: [
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.white.withAlpha(40),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Column(
            children: const [
              Icon(
                Icons.card_membership_outlined,
                color: Colors.white,
                size: 40,
              ),
              SizedBox(height: 12),
              Text(
                '您当前没有订阅计划',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              SizedBox(height: 6),
              Text(
                '订阅高级计划，解锁更多功能',
                style: TextStyle(
                  color: Colors.white70,
                  fontSize: 14,
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),
        AnimatedPressButton(
          onPressed: () => context.router.push(const SubscriptionPlansRoute()),
          child: const Text('查看订阅计划'),
          backgroundColor: Colors.white,
          textColor: AppColors.primaryColor,
        ),
      ],
    );
  }

  Widget _buildStatusBadge(SubscriptionStatus status) {
    Color color;
    String text;
    
    switch (status) {
      case SubscriptionStatus.active:
        color = Colors.green;
        text = '生效中';
        break;
      case SubscriptionStatus.trial:
        color = AppColors.secondaryColor;
        text = '试用中';
        break;
      case SubscriptionStatus.gracePeriod:
        color = Colors.orange;
        text = '宽限期';
        break;
      case SubscriptionStatus.cancelled:
        color = Colors.red.shade300;
        text = '已取消';
        break;
      case SubscriptionStatus.expired:
        color = Colors.red;
        text = '已过期';
        break;
      default:
        color = Colors.grey;
        text = '未知';
    }
    
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: color,
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(
        text,
        style: const TextStyle(
          color: Colors.white,
          fontSize: 10,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  Widget _buildRenewalInfo(Subscription subscription) {
    final formattedDate = subscription.nextBillingDate != null
        ? DateFormat('yyyy-MM-dd').format(subscription.nextBillingDate!)
        : '未知';
    
    return Container(
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: Colors.white.withAlpha(20),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: Colors.white.withAlpha(40),
          width: 1,
        ),
      ),
      child: Row(
        children: [
          const Icon(
            Icons.update,
            color: Colors.white70,
            size: 20,
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              '将于 $formattedDate 自动续费',
              style: const TextStyle(
                color: Colors.white,
                fontSize: 14,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildGracePeriodWarning() {
    return Container(
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: Colors.orange.withAlpha(40),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: Colors.orange.withAlpha(60),
          width: 1,
        ),
      ),
      child: Row(
        children: const [
          Icon(
            Icons.warning_amber_rounded,
            color: Colors.orange,
            size: 20,
          ),
          SizedBox(width: 10),
          Expanded(
            child: Text(
              '您的订阅已过期，正在宽限期内。请尽快续费以避免功能限制。',
              style: TextStyle(
                color: Colors.white,
                fontSize: 12,
              ),
            ),
          ),
        ],
      ),
    );
  }

  String _getSubscriptionPeriodText(Subscription subscription) {
    final startDate = DateFormat('yyyy-MM-dd').format(subscription.startDate);
    final endDate = DateFormat('yyyy-MM-dd').format(subscription.endDate);
    final cycle = subscription.billingCycle == BillingCycle.monthly ? '月' : '年';
    
    return '$startDate 至 $endDate·$cycle付';
  }

  IconData _getPlanIcon(String planId) {
    switch (planId) {
      case 'basic':
        return Icons.person_outline;
      case 'premium':
        return Icons.person;
      case 'family':
        return Icons.family_restroom;
      default:
        return Icons.card_membership;
    }
  }
} 