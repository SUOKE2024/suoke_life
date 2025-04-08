import 'package:flutter/material.dart';
import 'dart:ui'; // 添加dart:ui引入
import 'package:auto_route/auto_route.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/core/theme/app_colors.dart';
import 'package:suoke_life/presentation/home/widgets/ai_agent_avatar.dart';
import 'package:suoke_life/presentation/suoke/widgets/service_card.dart';
import 'package:suoke_life/core/widgets/app_widgets.dart';
import 'package:suoke_life/presentation/suoke/models/service_category.dart';
import 'package:suoke_life/presentation/suoke/models/service_item.dart';

/// SUOKE页面（服务频道）
@RoutePage()
class SuokePage extends ConsumerStatefulWidget {
  const SuokePage({super.key});

  @override
  ConsumerState<SuokePage> createState() => _SuokePageState();
}

class _SuokePageState extends ConsumerState<SuokePage> {
  // 服务分类
  final List<Map<String, dynamic>> _serviceCategories = [
    {
      'title': '健康咨询',
      'icon': Icons.health_and_safety,
      'color': Color(0xFF35BB78),
    },
    {
      'title': '农产品订购',
      'icon': Icons.shopping_basket,
      'color': Color(0xFFFF6800),
    },
    {
      'title': '农事体验',
      'icon': Icons.eco,
      'color': Color(0xFF6A88E5),
    },
    {
      'title': '健康培训',
      'icon': Icons.school,
      'color': Color(0xFF9E7FDE),
    },
  ];

  // 推荐健康服务
  final List<Map<String, dynamic>> _recommendedServices = [
    {
      'title': '中医体质咨询',
      'subtitle': '专业中医师一对一辨证',
      'price': '¥299',
      'rating': 4.9,
      'imageUrl':
          'https://images.unsplash.com/photo-1584515933487-779824d29309?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2940&q=80',
    },
    {
      'title': '有机蔬菜配送',
      'subtitle': '每周定期配送应季蔬果',
      'price': '¥198/周',
      'rating': 4.8,
      'imageUrl':
          'https://images.unsplash.com/photo-1592483648228-b35146a4330c?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2940&q=80',
    },
    {
      'title': '农场采摘体验',
      'subtitle': '亲近自然，采摘新鲜水果',
      'price': '¥168/人',
      'rating': 4.7,
      'imageUrl':
          'https://images.unsplash.com/photo-1526318472351-c75fcf070305?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2940&q=80',
    },
  ];

  // 热门健康服务
  final List<Map<String, dynamic>> _popularServices = [
    {
      'title': '中草药茶饮工坊',
      'subtitle': '学习自制养生茶饮',
      'price': '¥128/人',
      'imageUrl':
          'https://images.unsplash.com/photo-1564890369878-4f7b7d3c874b?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2940&q=80',
    },
    {
      'title': '私人健康管理',
      'subtitle': '全方位健康监测与指导',
      'price': '¥1998/年',
      'imageUrl':
          'https://images.unsplash.com/photo-1576091160550-2173dba999ef?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2940&q=80',
    },
    {
      'title': '食疗课程',
      'subtitle': '学习制作体质调理美食',
      'price': '¥268',
      'imageUrl':
          'https://images.unsplash.com/photo-1476718406336-bb5a9690ee2a?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2940&q=80',
    },
    {
      'title': '玉米迷宫门票',
      'subtitle': 'AR探宝+养生知识科普',
      'price': '¥88/人',
      'imageUrl':
          'https://images.unsplash.com/photo-1598517511269-bcee8f1b8069?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2940&q=80',
    },
  ];

  // 当前订单
  final List<Map<String, dynamic>> _currentOrders = [
    {
      'title': '中医体质咨询',
      'status': '已预约',
      'time': '2023-07-15 15:30',
      'location': '线上咨询',
    },
    {
      'title': '有机蔬菜配送',
      'status': '配送中',
      'time': '2023-07-12',
      'location': '送至默认地址',
    },
  ];

  // 模拟服务类别数据
  final List<ServiceCategory> _categories = [
    ServiceCategory(id: '1', name: '健康服务', icon: Icons.favorite),
    ServiceCategory(id: '2', name: '生活服务', icon: Icons.home),
    ServiceCategory(id: '3', name: '营养服务', icon: Icons.restaurant),
    ServiceCategory(id: '4', name: '运动服务', icon: Icons.directions_run),
    ServiceCategory(id: '5', name: '心理服务', icon: Icons.psychology),
    ServiceCategory(id: '6', name: '更多服务', icon: Icons.more_horiz),
  ];

  // 模拟推荐服务数据
  final List<ServiceItem> _recommendedServicesData = [
    ServiceItem(
      id: '0',
      name: '中医特色功能',
      description: '多模态智能诊断、舌诊、脉诊分析',
      iconData: Icons.health_and_safety,
      color: AppColors.primaryColor.withAlpha(220),
      routePath: '/tcm/features',
    ),
    ServiceItem(
      id: '1',
      name: '中医体质测评',
      description: '专业评估您的体质类型，提供个性化健康建议',
      iconData: Icons.accessibility_new,
      color: AppColors.primaryColor,
    ),
    ServiceItem(
      id: '2',
      name: '舌诊智能分析',
      description: '通过AI技术分析舌象，辅助健康评估',
      iconData: Icons.analytics,
      color: Colors.orange,
    ),
    ServiceItem(
      id: '3',
      name: '个性化营养方案',
      description: '根据体质和健康状况，定制专属营养方案',
      iconData: Icons.restaurant_menu,
      color: Colors.purple,
    ),
    ServiceItem(
      id: '4',
      name: '睡眠质量分析',
      description: '分析您的睡眠模式，提供改善建议',
      iconData: Icons.nightlight_round,
      color: Colors.indigo,
    ),
  ];

  @override
  Widget build(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      backgroundColor: Theme.of(context).colorScheme.background,
      appBar: AppBar(
        title: const Text('SUOKE'),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications_outlined),
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('消息通知功能正在开发中')),
              );
            },
          ),
          IconButton(
            icon: const Icon(Icons.person_outline),
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('个人中心功能正在开发中')),
              );
            },
          ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(height: 24),

              // 页面标题
              Text(
                'SUOKE服务',
                style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: isDarkMode
                          ? AppColors.darkTextPrimary
                          : AppColors.lightTextPrimary,
                    ),
              ),

              const SizedBox(height: 8),

              Text(
                '探索索克智能服务，助您健康生活',
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      color: isDarkMode
                          ? AppColors.darkTextSecondary
                          : AppColors.lightTextSecondary,
                    ),
              ),

              const SizedBox(height: 32),

              // 搜索框
              _buildSearchBar(),

              const SizedBox(height: 32),

              // 服务类别标题
              Text(
                '服务类别',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: isDarkMode
                          ? AppColors.darkTextPrimary
                          : AppColors.lightTextPrimary,
                    ),
              ),

              const SizedBox(height: 16),

              // 服务类别网格
              _buildCategoryGrid(),

              const SizedBox(height: 32),

              // 推荐服务标题
              Text(
                '推荐服务',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: isDarkMode
                          ? AppColors.darkTextPrimary
                          : AppColors.lightTextPrimary,
                    ),
              ),

              const SizedBox(height: 16),

              // 推荐服务列表
              _buildRecommendedServices(),

              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }

  // 构建搜索栏
  Widget _buildSearchBar() {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return Container(
      height: 54,
      decoration: BoxDecoration(
        color: isDarkMode
            ? Colors.grey.shade800.withAlpha(150)
            : Colors.grey.shade200.withAlpha(150),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withAlpha(10),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(16),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
          child: TextField(
            decoration: InputDecoration(
              hintText: '搜索服务...',
              hintStyle: TextStyle(
                color: isDarkMode ? Colors.grey.shade400 : Colors.grey.shade600,
              ),
              prefixIcon: Icon(
                Icons.search,
                color: isDarkMode ? Colors.grey.shade400 : Colors.grey.shade600,
              ),
              border: InputBorder.none,
              contentPadding:
                  const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
            ),
          ),
        ),
      ),
    );
  }

  // 构建服务类别网格
  Widget _buildCategoryGrid() {
    return GridView.count(
      crossAxisCount: 3,
      mainAxisSpacing: 16,
      crossAxisSpacing: 16,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      padding: EdgeInsets.zero,
      children:
          _categories.map((category) => _buildCategoryItem(category)).toList(),
    );
  }

  // 构建单个服务类别项
  Widget _buildCategoryItem(ServiceCategory category) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return BasicCard(
      title: category.name,
      onTap: () {
        // 处理类别点击事件
      },
      content: Container(
        height: 100,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              category.icon,
              size: 32,
              color: AppColors.primaryColor,
            ),
            const SizedBox(height: 8),
            Text(
              category.name,
              style: TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w500,
                color: isDarkMode
                    ? AppColors.darkTextPrimary
                    : AppColors.lightTextPrimary,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  // 构建推荐服务列表
  Widget _buildRecommendedServices() {
    return SizedBox(
      height: 200,
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        itemCount: _recommendedServicesData.length,
        itemBuilder: (context, index) {
          final service = _recommendedServicesData[index];
          return GestureDetector(
            onTap: () => _handleServiceTap(service),
            child: ServiceCard(
              title: service.name,
              description: service.description,
              icon: service.iconData,
              color: service.color,
              onTap: () => _handleServiceTap(service),
            ),
          );
        },
      ),
    );
  }

  // 处理服务点击
  void _handleServiceTap(ServiceItem service) {
    if (service.routePath != null && service.routePath!.isNotEmpty) {
      // 使用指定的路由路径
      context.router.pushNamed(service.routePath!);
      return;
    }
    
    // 兼容旧的路由逻辑
    switch (service.id) {
      case '1':
        // 中医体质测评
        context.router.pushNamed('/life/constitution-assessment');
        break;
      case '2':
        // 舌诊智能分析
        context.router.pushNamed('/suoke/tongue-diagnosis');
        break;
      case '3':
        // 个性化营养方案
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('个性化营养方案功能正在开发中')),
        );
        break;
      case '4':
        // 睡眠质量分析
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('睡眠质量分析功能正在开发中')),
        );
        break;
      default:
        // 其他服务
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('${service.name}功能正在开发中'),
            duration: const Duration(seconds: 2),
          ),
        );
        break;
    }
  }
}

/// 中医特色功能入口页面
@RoutePage()
class TcmFeaturesEntryPage extends StatelessWidget {
  const TcmFeaturesEntryPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('中医特色功能'),
        backgroundColor: AppColors.SUOKE_GREEN,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                '中医智能诊断',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 16),
              _buildFeatureCard(
                context,
                title: '多模态智能诊断',
                description: '结合舌诊、面诊、声音分析和症状描述，进行智能辨证分析',
                icon: Icons.health_and_safety,
                color: AppColors.SUOKE_GREEN,
                onTap: () => context.router.pushNamed('/tcm/multimodal-diagnosis'),
              ),
              const SizedBox(height: 16),
              _buildFeatureCard(
                context,
                title: '舌诊分析',
                description: '通过舌象分析体质特征和健康状态',
                icon: Icons.spa,
                color: const Color(0xFF4C8DAE),
                onTap: () => context.router.pushNamed('/tcm/tongue-diagnosis'),
              ),
              const SizedBox(height: 16),
              _buildFeatureCard(
                context,
                title: '脉诊分析',
                description: '通过脉象分析体内气血状态和脏腑功能',
                icon: Icons.favorite,
                color: const Color(0xFFFF6800),
                onTap: () => context.router.pushNamed('/tcm/pulse-diagnosis'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildFeatureCard(
    BuildContext context, {
    required String title,
    required String description,
    required IconData icon,
    required Color color,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [
              color,
              color.withAlpha(220),
            ],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: color.withAlpha(40),
              blurRadius: 8,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.white.withAlpha(50),
                  shape: BoxShape.circle,
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
                        color: Colors.white,
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      description,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 14,
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
      ),
    );
  }
}
