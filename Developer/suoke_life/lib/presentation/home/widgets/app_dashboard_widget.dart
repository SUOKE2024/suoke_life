import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:auto_route/auto_route.dart';
import '../../../core/router/app_router.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/widgets/animated_press_button.dart';
import '../../../domain/entities/app_dashboard.dart';
import '../../../di/providers/dashboard_providers.dart';

class AppDashboardWidget extends ConsumerWidget {
  const AppDashboardWidget({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final dashboardState = ref.watch(appDashboardProvider);
    final categories = ref.watch(appCategoriesProvider);
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.only(left: 16, right: 16, top: 8, bottom: 16),
          child: Text(
            '应用桌面',
            style: Theme.of(context).textTheme.headline6?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        
        dashboardState.when(
          data: (dashboard) {
            if (dashboard.items.isEmpty) {
              return _buildEmptyDashboard(context);
            }
            
            return _buildDashboardGrid(context, dashboard);
          },
          loading: () => const Center(
            child: CircularProgressIndicator(),
          ),
          error: (_, __) => Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Text('无法加载应用桌面'),
                const SizedBox(height: 8),
                TextButton(
                  onPressed: () => ref.refresh(appDashboardProvider),
                  child: const Text('重试'),
                ),
              ],
            ),
          ),
        ),
        
        const SizedBox(height: 24),
        
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Text(
            '全部应用',
            style: Theme.of(context).textTheme.headline6?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        
        const SizedBox(height: 12),
        
        categories.when(
          data: (categories) => _buildCategoriesGrid(context, categories),
          loading: () => const Center(
            child: CircularProgressIndicator(),
          ),
          error: (_, __) => Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Text('无法加载应用分类'),
                const SizedBox(height: 8),
                TextButton(
                  onPressed: () => ref.refresh(appCategoriesProvider),
                  child: const Text('重试'),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildEmptyDashboard(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.grey.withAlpha(30),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: Colors.grey.withAlpha(60),
          width: 1,
        ),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(
            Icons.dashboard_customize,
            size: 48,
            color: AppColors.primaryColor,
          ),
          const SizedBox(height: 16),
          const Text(
            '应用桌面暂无应用',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 8),
          const Text(
            '添加您常用的应用到桌面，让生活更高效',
            style: TextStyle(
              color: Colors.grey,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 16),
          AnimatedPressButton(
            onPressed: () => {},
            child: const Text('添加应用'),
            backgroundColor: AppColors.primaryColor,
            textColor: Colors.white,
          ),
        ],
      ),
    );
  }

  Widget _buildDashboardGrid(BuildContext context, AppDashboard dashboard) {
    // 4列网格
    const int columns = 4;
    
    // 计算需要多少行
    int rows = (dashboard.items.length / columns).ceil();
    
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      decoration: BoxDecoration(
        color: Colors.grey.withAlpha(15),
        borderRadius: BorderRadius.circular(16),
      ),
      child: GridView.builder(
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        padding: const EdgeInsets.all(12),
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: columns,
          childAspectRatio: 1,
          crossAxisSpacing: 12,
          mainAxisSpacing: 12,
        ),
        itemCount: dashboard.items.length,
        itemBuilder: (context, index) {
          final item = dashboard.items[index];
          return _buildWidgetItem(context, item);
        },
      ),
    );
  }

  Widget _buildWidgetItem(BuildContext context, DashboardItem item) {
    return GestureDetector(
      onTap: () => _handleWidgetTap(context, item),
      child: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withAlpha(10),
              blurRadius: 8,
              offset: const Offset(0, 3),
            ),
          ],
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Image.asset(
              item.widget.iconPath,
              width: 36,
              height: 36,
              errorBuilder: (context, error, stackTrace) => const Icon(
                Icons.widgets,
                size: 36,
                color: AppColors.primaryColor,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              item.widget.name,
              style: const TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.bold,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCategoriesGrid(BuildContext context, List<AppCategory> categories) {
    return SizedBox(
      height: 100,
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 12),
        itemCount: categories.length,
        itemBuilder: (context, index) {
          final category = categories[index];
          return _buildCategoryItem(context, category);
        },
      ),
    );
  }

  Widget _buildCategoryItem(BuildContext context, AppCategory category) {
    return GestureDetector(
      onTap: () => _handleCategoryTap(context, category),
      child: Container(
        width: 80,
        margin: const EdgeInsets.all(4),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 50,
              height: 50,
              decoration: BoxDecoration(
                color: category.color.withAlpha(30),
                shape: BoxShape.circle,
              ),
              child: Center(
                child: Image.asset(
                  category.iconPath,
                  width: 30,
                  height: 30,
                  errorBuilder: (context, error, stackTrace) => Icon(
                    Icons.category,
                    size: 30,
                    color: category.color,
                  ),
                ),
              ),
            ),
            const SizedBox(height: 8),
            Text(
              category.name,
              style: const TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.bold,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  void _handleWidgetTap(BuildContext context, DashboardItem item) {
    switch (item.widget.type) {
      case 'health_stats':
        context.router.push(const HealthStatsRoute());
        break;
      case 'tcm_constitution':
        context.router.push(const ConstitutionRoute());
        break;
      case 'daily_recommendation':
        context.router.push(const DailyRecommendationRoute());
        break;
      case 'points_summary':
        context.router.push(const PointsHistoryRoute());
        break;
      case 'subscription_status':
        context.router.push(const SubscriptionDetailsRoute());
        break;
      case 'recent_activity':
        context.router.push(const ActivityHistoryRoute());
        break;
      case 'seasonal_advice':
        context.router.push(const SeasonalAdviceRoute());
        break;
      default:
        // 未知的小部件类型，可以显示通用详情页或提示
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('${item.widget.name} 功能即将上线')),
        );
    }
  }

  void _handleCategoryTap(BuildContext context, AppCategory category) {
    switch (category.id) {
      case 'health':
        context.router.push(const HealthHomeRoute());
        break;
      case 'tcm':
        context.router.push(const TcmHomeRoute());
        break;
      case 'shopping':
        context.router.push(const ShoppingHomeRoute());
        break;
      case 'community':
        context.router.push(const CommunityHomeRoute());
        break;
      default:
        // 未知的分类，可以显示通用分类页或提示
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('${category.name} 分类即将上线')),
        );
    }
  }
}