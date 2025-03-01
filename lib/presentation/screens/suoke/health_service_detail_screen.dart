import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:auto_route/auto_route.dart';

import '../../../domain/entities/health_service.dart';
import '../../providers/health_providers.dart';
import '../../widgets/loading_overlay.dart';
import '../../widgets/error_view.dart';

@RoutePage()
class HealthServiceDetailScreen extends ConsumerStatefulWidget {
  final String serviceId;

  const HealthServiceDetailScreen({
    Key? key,
    @PathParam('id') required this.serviceId,
  }) : super(key: key);

  @override
  ConsumerState<HealthServiceDetailScreen> createState() => _HealthServiceDetailScreenState();
}

class _HealthServiceDetailScreenState extends ConsumerState<HealthServiceDetailScreen> {
  @override
  void initState() {
    super.initState();
    // 加载服务详情
    Future.microtask(() => 
      ref.read(healthServiceDetailProvider.notifier).loadServiceDetail(widget.serviceId)
    );
  }

  @override
  Widget build(BuildContext context) {
    final serviceDetailState = ref.watch(healthServiceDetailProvider);
    
    return Scaffold(
      body: LoadingOverlay(
        isLoading: serviceDetailState.isLoading,
        child: serviceDetailState.error != null
            ? ErrorView(
                error: serviceDetailState.error!,
                onRetry: () => ref.read(healthServiceDetailProvider.notifier)
                    .loadServiceDetail(widget.serviceId),
              )
            : serviceDetailState.service != null
                ? _buildServiceDetail(serviceDetailState.service!)
                : const SizedBox.shrink(),
      ),
    );
  }

  Widget _buildServiceDetail(HealthService service) {
    return CustomScrollView(
      slivers: [
        // 顶部应用栏
        SliverAppBar(
          expandedHeight: 200,
          pinned: true,
          flexibleSpace: FlexibleSpaceBar(
            title: Text(
              service.name,
              style: const TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
              ),
            ),
            background: Stack(
              fit: StackFit.expand,
              children: [
                // 服务图片
                Image.network(
                  service.imageUrl,
                  fit: BoxFit.cover,
                  errorBuilder: (context, error, stackTrace) => Container(
                    color: Theme.of(context).primaryColor,
                    child: const Icon(
                      Icons.healing,
                      size: 80,
                      color: Colors.white,
                    ),
                  ),
                ),
                // 渐变遮罩
                const DecoratedBox(
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.topCenter,
                      end: Alignment.bottomCenter,
                      colors: [
                        Colors.transparent,
                        Colors.black54,
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
          actions: [
            IconButton(
              icon: const Icon(Icons.share),
              onPressed: () {
                // 分享功能
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('分享功能即将上线')),
                );
              },
            ),
            IconButton(
              icon: const Icon(Icons.favorite_border),
              onPressed: () {
                // 收藏功能
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('收藏功能即将上线')),
                );
              },
            ),
          ],
        ),
        
        // 服务内容
        SliverToBoxAdapter(
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // 价格和评分
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    // 价格
                    Text(
                      '¥${service.price.toStringAsFixed(2)}',
                      style: const TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                        color: Colors.red,
                      ),
                    ),
                    // 评分
                    Row(
                      children: [
                        const Icon(Icons.star, color: Colors.amber),
                        const SizedBox(width: 4),
                        Text(
                          '${service.rating}',
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Text(
                          ' (${service.reviewCount}条评价)',
                          style: TextStyle(
                            fontSize: 14,
                            color: Colors.grey[600],
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
                
                const SizedBox(height: 16),
                
                // 服务类型和时长
                Row(
                  children: [
                    Chip(
                      label: Text(service.type),
                      backgroundColor: Theme.of(context).primaryColor.withOpacity(0.1),
                      avatar: Icon(
                        _getServiceTypeIcon(service.type),
                        color: Theme.of(context).primaryColor,
                        size: 16,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Chip(
                      label: Text('${service.durationMinutes}分钟'),
                      backgroundColor: Theme.of(context).primaryColor.withOpacity(0.1),
                      avatar: Icon(
                        Icons.timer,
                        color: Theme.of(context).primaryColor,
                        size: 16,
                      ),
                    ),
                  ],
                ),
                
                const SizedBox(height: 24),
                
                // 服务描述
                const Text(
                  '服务描述',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  service.description,
                  style: const TextStyle(
                    fontSize: 16,
                    height: 1.5,
                  ),
                ),
                
                const SizedBox(height: 24),
                
                // 服务内容
                const Text(
                  '服务内容',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                ...service.features.map((feature) => Padding(
                  padding: const EdgeInsets.only(bottom: 8.0),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Icon(
                        Icons.check_circle,
                        color: Colors.green,
                        size: 20,
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          feature,
                          style: const TextStyle(fontSize: 16),
                        ),
                      ),
                    ],
                  ),
                )),
                
                const SizedBox(height: 24),
                
                // 服务提供者
                const Text(
                  '服务提供者',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                Card(
                  elevation: 2,
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Row(
                      children: [
                        CircleAvatar(
                          radius: 30,
                          backgroundImage: NetworkImage(service.providerImageUrl),
                          onBackgroundImageError: (_, __) {},
                          child: service.providerImageUrl.isEmpty
                              ? const Icon(Icons.person, size: 30)
                              : null,
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                service.providerName,
                                style: const TextStyle(
                                  fontSize: 18,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                service.providerDescription,
                                style: TextStyle(
                                  fontSize: 14,
                                  color: Colors.grey[600],
                                ),
                              ),
                            ],
                          ),
                        ),
                        IconButton(
                          icon: const Icon(Icons.message),
                          onPressed: () {
                            // 联系服务提供者
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(content: Text('联系功能即将上线')),
                            );
                          },
                        ),
                      ],
                    ),
                  ),
                ),
                
                const SizedBox(height: 24),
                
                // 用户评价
                const Text(
                  '用户评价',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                service.reviews.isNotEmpty
                    ? Column(
                        children: service.reviews.map((review) => Padding(
                          padding: const EdgeInsets.only(bottom: 16.0),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                children: [
                                  CircleAvatar(
                                    radius: 20,
                                    backgroundImage: NetworkImage(review.userAvatarUrl),
                                    onBackgroundImageError: (_, __) {},
                                    child: review.userAvatarUrl.isEmpty
                                        ? const Icon(Icons.person, size: 20)
                                        : null,
                                  ),
                                  const SizedBox(width: 8),
                                  Text(
                                    review.userName,
                                    style: const TextStyle(
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                  const Spacer(),
                                  Row(
                                    children: List.generate(
                                      5,
                                      (index) => Icon(
                                        index < review.rating ? Icons.star : Icons.star_border,
                                        color: Colors.amber,
                                        size: 16,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 8),
                              Text(review.comment),
                              const SizedBox(height: 4),
                              Text(
                                review.date,
                                style: TextStyle(
                                  fontSize: 12,
                                  color: Colors.grey[600],
                                ),
                              ),
                              const Divider(),
                            ],
                          ),
                        )).toList(),
                      )
                    : const Center(
                        child: Padding(
                          padding: EdgeInsets.all(16.0),
                          child: Text('暂无评价'),
                        ),
                      ),
              ],
            ),
          ),
        ),
      ],
    );
  }
  
  // 根据服务类型获取对应图标
  IconData _getServiceTypeIcon(String type) {
    switch (type.toLowerCase()) {
      case '中医诊断':
        return Icons.medical_services;
      case '健康咨询':
        return Icons.health_and_safety;
      case '营养指导':
        return Icons.restaurant;
      case '运动指导':
        return Icons.fitness_center;
      case '心理咨询':
        return Icons.psychology;
      default:
        return Icons.healing;
    }
  }
}

// 底部预约按钮
class _BottomAppointmentButton extends StatelessWidget {
  final HealthService service;
  
  const _BottomAppointmentButton({
    Key? key,
    required this.service,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 10,
            offset: const Offset(0, -5),
          ),
        ],
      ),
      child: Row(
        children: [
          Expanded(
            child: ElevatedButton(
              onPressed: () {
                // 预约服务
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('预约功能即将上线')),
                );
              },
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
              child: const Text(
                '立即预约',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
} 