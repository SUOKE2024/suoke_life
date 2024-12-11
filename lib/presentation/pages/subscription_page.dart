import 'package:flutter/material.dart';

import '../../services/subscription_service.dart';
import '../../services/payment_service.dart';

class SubscriptionPage extends StatelessWidget {
  const SubscriptionPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('会员订阅'),
      ),
      body: Consumer<SubscriptionService>(
        builder: (context, subscriptionService, child) {
          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              _buildCurrentPlanCard(context, subscriptionService),
              const SizedBox(height: 24),
              _buildPlanList(context, subscriptionService),
            ],
          );
        },
      ),
    );
  }

  Widget _buildCurrentPlanCard(
    BuildContext context,
    SubscriptionService subscriptionService,
  ) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '当前方案',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            Text(
              subscriptionService.currentPlan.toString().split('.').last,
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            if (subscriptionService.expiryDate != null) ...[
              const SizedBox(height: 8),
              Text(
                '到期时间: ${subscriptionService.expiryDate!.toString().split(' ')[0]}',
                style: Theme.of(context).textTheme.bodyMedium,
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildPlanList(
    BuildContext context,
    SubscriptionService subscriptionService,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '升级方案',
          style: Theme.of(context).textTheme.titleLarge,
        ),
        const SizedBox(height: 16),
        ...SubscriptionPlan.values.map((plan) {
          final features = SubscriptionService.planFeatures[plan]!;
          return Card(
            margin: const EdgeInsets.only(bottom: 16),
            child: InkWell(
              onTap: () => _handleUpgrade(context, plan),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          plan.toString().split('.').last,
                          style: Theme.of(context).textTheme.titleMedium,
                        ),
                        Text(
                          _getPlanPrice(plan),
                          style: Theme.of(context).textTheme.titleMedium,
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    _buildFeatureList(features),
                  ],
                ),
              ),
            ),
          );
        }).toList(),
      ],
    );
  }

  Widget _buildFeatureList(SubscriptionFeatures features) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildFeatureItem(
          '每日AI对话次数',
          features.dailyAIQuota == -1 ? '无限制' : '${features.dailyAIQuota}次',
        ),
        _buildFeatureItem('视频会诊', features.videoConsultation ? '支持' : '不支持'),
        _buildFeatureItem('专家匹配', features.expertMatching ? '支持' : '不支持'),
        _buildFeatureItem('定制服务', features.customService ? '支持' : '不支持'),
      ],
    );
  }

  Widget _buildFeatureItem(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          const Icon(Icons.check_circle_outline, size: 16),
          const SizedBox(width: 8),
          Text(label),
          const Spacer(),
          Text(value),
        ],
      ),
    );
  }

  String _getPlanPrice(SubscriptionPlan plan) {
    switch (plan) {
      case SubscriptionPlan.basic:
        return '免费';
      case SubscriptionPlan.pro:
        return '¥99/月';
      case SubscriptionPlan.enterprise:
        return '¥999/月';
    }
  }

  void _handleUpgrade(BuildContext context, SubscriptionPlan plan) async {
    if (plan == Provider.of<SubscriptionService>(context, listen: false).currentPlan) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('您已经是该方案用户')),
      );
      return;
    }

    final paymentService = Provider.of<PaymentService>(context, listen: false);
    final subscriptionService = Provider.of<SubscriptionService>(context, listen: false);

    try {
      // 创建订单
      final order = await paymentService.createOrder(
        amount: _getPlanAmount(plan),
        productId: plan.toString(),
        userId: 'current_user_id', // TODO: 获取实际用户ID
        method: PaymentMethod.alipay, // TODO: 让用户选择支付方式
      );

      // 处理支付
      final success = await paymentService.processPayment(order);
      if (success) {
        await subscriptionService.upgradePlan(plan);
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('升级成功')),
          );
        }
      } else {
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('支付失败，请重试')),
          );
        }
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('操作失败，请重试')),
        );
      }
    }
  }

  double _getPlanAmount(SubscriptionPlan plan) {
    switch (plan) {
      case SubscriptionPlan.basic:
        return 0;
      case SubscriptionPlan.pro:
        return 99;
      case SubscriptionPlan.enterprise:
        return 999;
    }
  }
} 