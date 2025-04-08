import 'package:dartz/dartz.dart';
import '../entities/app_dashboard.dart';
import '../../core/utils/failure.dart';

/// 桌面应用仓库接口
abstract class DashboardRepository {
  /// 获取用户当前桌面配置
  Future<Either<Failure, AppDashboard>> getUserDashboard();
  
  /// 更新用户桌面配置
  Future<Either<Failure, AppDashboard>> updateDashboard(AppDashboard dashboard);
  
  /// 添加小部件到桌面
  Future<Either<Failure, AppDashboard>> addWidget(AppWidget widget, {int row = 0, int column = 0});
  
  /// 从桌面移除小部件
  Future<Either<Failure, AppDashboard>> removeWidget(String widgetId);
  
  /// 移动小部件位置
  Future<Either<Failure, AppDashboard>> moveWidgetPosition(String widgetId, {required int newRow, required int newColumn});
  
  /// 调整小部件大小
  Future<Either<Failure, AppDashboard>> resizeWidget(String widgetId, {required int rowSpan, required int columnSpan});
  
  /// 获取所有应用分类
  Future<Either<Failure, List<AppCategory>>> getAppCategories();
  
  /// 根据分类获取应用小部件
  Future<Either<Failure, List<AppWidget>>> getAppWidgetsByCategory(String categoryId);
  
  /// 搜索应用小部件
  Future<Either<Failure, List<AppWidget>>> searchAppWidgets(String query);
  
  /// 重置桌面为默认布局
  Future<Either<Failure, AppDashboard>> resetDashboardToDefault();
  
  /// 获取推荐的小部件
  Future<Either<Failure, List<AppWidget>>> getRecommendedWidgets();
  
  /// 保存自定义布局
  Future<Either<Failure, bool>> saveCustomLayout(String layoutName, AppDashboard dashboard);
  
  /// 加载自定义布局
  Future<Either<Failure, AppDashboard>> loadCustomLayout(String layoutId);
  
  /// 获取所有自定义布局
  Future<Either<Failure, List<SavedLayout>>> getSavedLayouts();
  
  /// 删除自定义布局
  Future<Either<Failure, bool>> deleteCustomLayout(String layoutId);
}

/// 数据源接口 - 远程
abstract class DashboardRemoteDataSource {
  Future<AppDashboard> getUserDashboard();
  Future<AppDashboard> updateDashboard(AppDashboard dashboard);
  Future<AppDashboard> addWidget(AppWidget widget, {int row = 0, int column = 0});
  Future<AppDashboard> removeWidget(String widgetId);
  Future<AppDashboard> moveWidgetPosition(String widgetId, {required int newRow, required int newColumn});
  Future<AppDashboard> resizeWidget(String widgetId, {required int rowSpan, required int columnSpan});
  Future<List<AppCategory>> getAppCategories();
  Future<List<AppWidget>> getAppWidgetsByCategory(String categoryId);
  Future<List<AppWidget>> searchAppWidgets(String query);
  Future<AppDashboard> resetDashboardToDefault();
  Future<List<AppWidget>> getRecommendedWidgets();
  Future<bool> saveCustomLayout(String layoutName, AppDashboard dashboard);
  Future<AppDashboard> loadCustomLayout(String layoutId);
  Future<List<SavedLayout>> getSavedLayouts();
  Future<bool> deleteCustomLayout(String layoutId);
}

/// 数据源接口 - 本地
abstract class DashboardLocalDataSource {
  Future<AppDashboard?> getCachedDashboard();
  Future<void> cacheDashboard(AppDashboard dashboard);
  Future<List<AppCategory>?> getCachedCategories();
  Future<void> cacheCategories(List<AppCategory> categories);
  Future<List<SavedLayout>?> getCachedLayouts();
  Future<void> cacheLayouts(List<SavedLayout> layouts);
  Future<void> clearCache();
}

/// 保存的自定义布局
class SavedLayout {
  final String id;
  final String name;
  final DateTime createdAt;
  final AppDashboard dashboard;

  SavedLayout({
    required this.id,
    required this.name,
    required this.createdAt,
    required this.dashboard,
  });
} 