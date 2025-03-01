import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../domain/entities/health_service.dart';
import '../../../di/providers/health_service_providers.dart';
import '../../widgets/health_service_card.dart';
import '../../widgets/service_section.dart';
import '../../widgets/service_search_bar.dart';

@RoutePage()
class SuokeTabScreen extends ConsumerStatefulWidget {
  const SuokeTabScreen({Key? key}) : super(key: key);

  @override
  ConsumerState<SuokeTabScreen> createState() => _SuokeTabScreenState();
}

class _SuokeTabScreenState extends ConsumerState<SuokeTabScreen> {
  final TextEditingController _searchController = TextEditingController();
  
  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }
  
  @override
  Widget build(BuildContext context) {
    final healthServiceState = ref.watch(healthServiceProvider);
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('SUOKE'),
        centerTitle: true,
      ),
      body: healthServiceState.isLoading
          ? const Center(child: CircularProgressIndicator())
          : healthServiceState.error != null
              ? _buildErrorView(healthServiceState.error!)
              : _buildServiceListView(healthServiceState),
    );
  }
  
  Widget _buildErrorView(String error) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(
            Icons.error_outline,
            size: 60,
            color: Colors.red,
          ),
          const SizedBox(height: 16),
          Text(
            '加载服务失败',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const SizedBox(height: 8),
          Text(
            error,
            style: Theme.of(context).textTheme.bodyMedium,
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 24),
          ElevatedButton(
            onPressed: () {
              // 重新加载服务
              ref.refresh(healthServiceProvider);
            },
            child: const Text('重试'),
          ),
        ],
      ),
    );
  }
  
  Widget _buildServiceListView(HealthServiceState state) {
    return RefreshIndicator(
      onRefresh: () async {
        // 下拉刷新
        ref.refresh(healthServiceProvider);
      },
      child: ListView(
        children: [
          ServiceSearchBar(
            controller: _searchController,
            onSubmitted: (query) {
              // 处理搜索
              final results = ref.read(healthServiceProvider.notifier).searchServices(query);
              _showSearchResults(results);
            },
            onFilterPressed: () {
              // 显示筛选选项
              _showFilterOptions();
            },
          ),
          _buildBanner(),
          _buildRecentlyUsedServices(state.recentlyUsedServices),
          _buildFeaturedServices(state.featuredServices),
          _buildServiceCategories(),
          _buildAllServices(state.allServices),
        ],
      ),
    );
  }
  
  Widget _buildBanner() {
    return Container(
      height: 160,
      margin: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(12),
        gradient: LinearGradient(
          colors: [
            Colors.green.shade400,
            Colors.green.shade700,
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
      ),
      child: Stack(
        children: [
          Positioned.fill(
            child: ClipRRect(
              borderRadius: BorderRadius.circular(12),
              child: Opacity(
                opacity: 0.1,
                child: Image.asset(
                  'assets/images/banner_pattern.png',
                  fit: BoxFit.cover,
                  errorBuilder: (context, error, stackTrace) {
                    return const SizedBox(); // 空白占位
                  },
                ),
              ),
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  '立刻开始您的健康旅程',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 8),
                const Text(
                  '专业健康服务，为您定制健康生活方案',
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.white,
                  ),
                ),
                const Spacer(),
                ElevatedButton(
                  onPressed: () {
                    // 开始健康评估
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.white,
                    foregroundColor: Colors.green.shade700,
                  ),
                  child: const Text('开始健康评估'),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildRecentlyUsedServices(List<HealthService> services) {
    if (services.isEmpty) return const SizedBox.shrink();
    
    return ServiceSection(
      title: '最近使用',
      subtitle: '您最近使用的健康服务',
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      children: services
          .map((service) => HealthServiceCard(
                service: service,
                onTap: () => _navigateToServiceDetail(service),
                isHorizontal: true,
              ))
          .toList(),
      isScrollable: false,
    );
  }
  
  Widget _buildFeaturedServices(List<HealthService> services) {
    return ServiceSection(
      title: '推荐服务',
      subtitle: '为您精选的健康服务',
      children: services
          .map((service) => HealthServiceCard(
                service: service,
                onTap: () => _navigateToServiceDetail(service),
              ))
          .toList(),
      onViewMore: () {
        // 查看更多推荐服务
      },
    );
  }
  
  Widget _buildServiceCategories() {
    final categories = [
      {'icon': Icons.visibility, 'title': '中医诊断', 'type': HealthServiceType.tcmDiagnosis},
      {'icon': Icons.assessment, 'title': '健康评估', 'type': HealthServiceType.healthAssessment},
      {'icon': Icons.restaurant, 'title': '膳食指导', 'type': HealthServiceType.dietGuidance},
      {'icon': Icons.directions_run, 'title': '运动处方', 'type': HealthServiceType.exercisePrescription},
      {'icon': Icons.bedtime, 'title': '睡眠改善', 'type': HealthServiceType.sleepImprovement},
      {'icon': Icons.psychology, 'title': '心理调适', 'type': HealthServiceType.mentalWellness},
      {'icon': Icons.monitor_heart, 'title': '慢病管理', 'type': HealthServiceType.chronicDiseaseManagement},
      {'icon': Icons.health_and_safety, 'title': '亚健康调理', 'type': HealthServiceType.subhealthConditioning},
    ];
    
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            '服务分类',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          GridView.builder(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 4,
              childAspectRatio: 1,
              crossAxisSpacing: 16,
              mainAxisSpacing: 16,
            ),
            itemCount: categories.length,
            itemBuilder: (context, index) {
              final category = categories[index];
              return _buildCategoryItem(
                icon: category['icon'] as IconData,
                title: category['title'] as String,
                onTap: () => _filterServicesByType(category['type'] as HealthServiceType),
              );
            },
          ),
        ],
      ),
    );
  }
  
  Widget _buildCategoryItem({
    required IconData icon,
    required String title,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            width: 50,
            height: 50,
            decoration: BoxDecoration(
              color: Colors.green.withOpacity(0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(
              icon,
              color: Colors.green,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            title,
            style: const TextStyle(fontSize: 12),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
  
  Widget _buildAllServices(List<HealthService> services) {
    return ServiceSection(
      title: '所有服务',
      isScrollable: false,
      children: services
          .map((service) => HealthServiceCard(
                service: service,
                onTap: () => _navigateToServiceDetail(service),
                isHorizontal: true,
              ))
          .toList(),
    );
  }
  
  void _navigateToServiceDetail(HealthService service) {
    // 记录服务使用
    ref.read(healthServiceProvider.notifier).recordServiceUsage(service);
    
    // 导航到服务详情页
    // context.router.push(ServiceDetailRoute(serviceId: service.id));
    
    // 临时用对话框显示
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(service.name),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(service.description),
            const SizedBox(height: 16),
            Row(
              children: [
                const Text('价格: '),
                Text(
                  service.price == 0 ? '免费' : '¥${service.price.toStringAsFixed(1)}',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: service.price == 0 ? Colors.green : Colors.orange,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              children: service.tags
                  .map((tag) => Chip(
                        label: Text(tag),
                        backgroundColor: Colors.blue.withOpacity(0.1),
                        labelStyle: const TextStyle(
                          color: Colors.blue,
                          fontSize: 12,
                        ),
                      ))
                  .toList(),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('关闭'),
          ),
          FilledButton(
            onPressed: () {
              Navigator.of(context).pop();
              // 跳转到服务详情页
              // 这里暂时不实现
            },
            child: const Text('立即使用'),
          ),
        ],
      ),
    );
  }
  
  void _showSearchResults(List<HealthService> results) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) {
        return DraggableScrollableSheet(
          initialChildSize: 0.7,
          minChildSize: 0.5,
          maxChildSize: 0.9,
          expand: false,
          builder: (context, scrollController) {
            return Column(
              children: [
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: Row(
                    children: [
                      Text(
                        '搜索结果: ${results.length}个服务',
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const Spacer(),
                      IconButton(
                        icon: const Icon(Icons.close),
                        onPressed: () => Navigator.pop(context),
                      ),
                    ],
                  ),
                ),
                const Divider(),
                Expanded(
                  child: results.isEmpty
                      ? const Center(
                          child: Text('没有找到相关服务'),
                        )
                      : ListView.separated(
                          controller: scrollController,
                          itemCount: results.length,
                          separatorBuilder: (context, index) => const Divider(),
                          itemBuilder: (context, index) {
                            final service = results[index];
                            return ListTile(
                              leading: CircleAvatar(
                                backgroundColor: Colors.green.withOpacity(0.1),
                                child: Icon(
                                  service.icon,
                                  color: Colors.green,
                                ),
                              ),
                              title: Text(service.name),
                              subtitle: Text(
                                service.description,
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                              ),
                              trailing: Text(
                                service.price == 0 ? '免费' : '¥${service.price.toStringAsFixed(1)}',
                                style: TextStyle(
                                  fontWeight: FontWeight.bold,
                                  color: service.price == 0 ? Colors.green : Colors.orange,
                                ),
                              ),
                              onTap: () {
                                Navigator.pop(context);
                                _navigateToServiceDetail(service);
                              },
                            );
                          },
                        ),
                ),
              ],
            );
          },
        );
      },
    );
  }
  
  void _showFilterOptions() {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) {
        return Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                '筛选服务',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 16),
              const Text(
                '价格',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton(
                      onPressed: () => _filterServicesByPrice(isPremium: false),
                      child: const Text('免费服务'),
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: OutlinedButton(
                      onPressed: () => _filterServicesByPrice(isPremium: true),
                      child: const Text('付费服务'),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              const Text(
                '服务类型',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  FilterChip(
                    label: const Text('中医诊断'),
                    onSelected: (selected) {
                      if (selected) {
                        Navigator.pop(context);
                        _filterServicesByType(HealthServiceType.tcmDiagnosis);
                      }
                    },
                  ),
                  FilterChip(
                    label: const Text('健康评估'),
                    onSelected: (selected) {
                      if (selected) {
                        Navigator.pop(context);
                        _filterServicesByType(HealthServiceType.healthAssessment);
                      }
                    },
                  ),
                  FilterChip(
                    label: const Text('膳食指导'),
                    onSelected: (selected) {
                      if (selected) {
                        Navigator.pop(context);
                        _filterServicesByType(HealthServiceType.dietGuidance);
                      }
                    },
                  ),
                  FilterChip(
                    label: const Text('运动处方'),
                    onSelected: (selected) {
                      if (selected) {
                        Navigator.pop(context);
                        _filterServicesByType(HealthServiceType.exercisePrescription);
                      }
                    },
                  ),
                  FilterChip(
                    label: const Text('睡眠改善'),
                    onSelected: (selected) {
                      if (selected) {
                        Navigator.pop(context);
                        _filterServicesByType(HealthServiceType.sleepImprovement);
                      }
                    },
                  ),
                  FilterChip(
                    label: const Text('心理调适'),
                    onSelected: (selected) {
                      if (selected) {
                        Navigator.pop(context);
                        _filterServicesByType(HealthServiceType.mentalWellness);
                      }
                    },
                  ),
                  FilterChip(
                    label: const Text('慢病管理'),
                    onSelected: (selected) {
                      if (selected) {
                        Navigator.pop(context);
                        _filterServicesByType(HealthServiceType.chronicDiseaseManagement);
                      }
                    },
                  ),
                  FilterChip(
                    label: const Text('亚健康调理'),
                    onSelected: (selected) {
                      if (selected) {
                        Navigator.pop(context);
                        _filterServicesByType(HealthServiceType.subhealthConditioning);
                      }
                    },
                  ),
                ],
              ),
              const SizedBox(height: 16),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: () => Navigator.pop(context),
                  child: const Text('关闭'),
                ),
              ),
            ],
          ),
        );
      },
    );
  }
  
  void _filterServicesByType(HealthServiceType type) {
    final services = ref.read(healthServiceProvider.notifier).filterServicesByType(type);
    
    _showFilteredServices(
      title: _getServiceTypeName(type) + '服务',
      services: services,
    );
  }
  
  void _filterServicesByPrice({required bool isPremium}) {
    Navigator.pop(context);
    
    final services = ref.read(healthServiceProvider.notifier).filterServicesByPrice(isPremium: isPremium);
    
    _showFilteredServices(
      title: isPremium ? '付费服务' : '免费服务',
      services: services,
    );
  }
  
  void _showFilteredServices({
    required String title,
    required List<HealthService> services,
  }) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) {
        return DraggableScrollableSheet(
          initialChildSize: 0.7,
          minChildSize: 0.5,
          maxChildSize: 0.9,
          expand: false,
          builder: (context, scrollController) {
            return Column(
              children: [
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: Row(
                    children: [
                      Text(
                        '$title (${services.length})',
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const Spacer(),
                      IconButton(
                        icon: const Icon(Icons.close),
                        onPressed: () => Navigator.pop(context),
                      ),
                    ],
                  ),
                ),
                const Divider(),
                Expanded(
                  child: services.isEmpty
                      ? const Center(
                          child: Text('没有找到相关服务'),
                        )
                      : ListView.separated(
                          controller: scrollController,
                          itemCount: services.length,
                          separatorBuilder: (context, index) => const Divider(),
                          itemBuilder: (context, index) {
                            final service = services[index];
                            return ListTile(
                              leading: CircleAvatar(
                                backgroundColor: Colors.green.withOpacity(0.1),
                                child: Icon(
                                  service.icon,
                                  color: Colors.green,
                                ),
                              ),
                              title: Text(service.name),
                              subtitle: Text(
                                service.description,
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                              ),
                              trailing: Text(
                                service.price == 0 ? '免费' : '¥${service.price.toStringAsFixed(1)}',
                                style: TextStyle(
                                  fontWeight: FontWeight.bold,
                                  color: service.price == 0 ? Colors.green : Colors.orange,
                                ),
                              ),
                              onTap: () {
                                Navigator.pop(context);
                                _navigateToServiceDetail(service);
                              },
                            );
                          },
                        ),
                ),
              ],
            );
          },
        );
      },
    );
  }
  
  String _getServiceTypeName(HealthServiceType type) {
    switch (type) {
      case HealthServiceType.tcmDiagnosis:
        return '中医诊断';
      case HealthServiceType.healthAssessment:
        return '健康评估';
      case HealthServiceType.dietGuidance:
        return '膳食指导';
      case HealthServiceType.exercisePrescription:
        return '运动处方';
      case HealthServiceType.sleepImprovement:
        return '睡眠改善';
      case HealthServiceType.mentalWellness:
        return '心理调适';
      case HealthServiceType.chronicDiseaseManagement:
        return '慢病管理';
      case HealthServiceType.subhealthConditioning:
        return '亚健康调理';
    }
  }
}