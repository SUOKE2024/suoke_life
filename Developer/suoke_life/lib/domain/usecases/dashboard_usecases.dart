import 'package:dartz/dartz.dart';
import '../entities/app_dashboard.dart';
import '../repositories/dashboard_repository.dart';
import '../../core/utils/failure.dart';

// 获取用户桌面用例
class GetUserDashboardUseCase {
  final DashboardRepository repository;

  GetUserDashboardUseCase({required this.repository});

  Future<Either<Failure, AppDashboard>> call() async {
    return await repository.getUserDashboard();
  }
}

// 更新桌面用例
class UpdateDashboardUseCase {
  final DashboardRepository repository;

  UpdateDashboardUseCase({required this.repository});

  Future<Either<Failure, AppDashboard>> call(AppDashboard dashboard) async {
    return await repository.updateDashboard(dashboard);
  }
}

// 添加桌面小部件用例
class AddDashboardWidgetUseCase {
  final DashboardRepository repository;

  AddDashboardWidgetUseCase({required this.repository});

  Future<Either<Failure, AppDashboard>> call(AppWidget widget, {int row = 0, int column = 0}) async {
    return await repository.addWidget(widget, row: row, column: column);
  }
}

// 移除桌面小部件用例
class RemoveDashboardWidgetUseCase {
  final DashboardRepository repository;

  RemoveDashboardWidgetUseCase({required this.repository});

  Future<Either<Failure, AppDashboard>> call(String widgetId) async {
    return await repository.removeWidget(widgetId);
  }
}

// 获取应用分类用例
class GetAppCategoriesUseCase {
  final DashboardRepository repository;

  GetAppCategoriesUseCase({required this.repository});

  Future<Either<Failure, List<AppCategory>>> call() async {
    return await repository.getAppCategories();
  }
}

// 根据分类获取应用用例
class GetAppWidgetsByCategoryUseCase {
  final DashboardRepository repository;

  GetAppWidgetsByCategoryUseCase({required this.repository});

  Future<Either<Failure, List<AppWidget>>> call(String categoryId) async {
    return await repository.getAppWidgetsByCategory(categoryId);
  }
}

// 移动桌面小部件位置用例
class MoveWidgetPositionUseCase {
  final DashboardRepository repository;

  MoveWidgetPositionUseCase({required this.repository});

  Future<Either<Failure, AppDashboard>> call(String widgetId, {required int newRow, required int newColumn}) async {
    return await repository.moveWidgetPosition(widgetId, newRow: newRow, newColumn: newColumn);
  }
}

// 重置桌面为默认布局用例
class ResetDashboardToDefaultUseCase {
  final DashboardRepository repository;

  ResetDashboardToDefaultUseCase({required this.repository});

  Future<Either<Failure, AppDashboard>> call() async {
    return await repository.resetDashboardToDefault();
  }
}

// 调整小部件大小用例
class ResizeWidgetUseCase {
  final DashboardRepository repository;

  ResizeWidgetUseCase({required this.repository});

  Future<Either<Failure, AppDashboard>> call(String widgetId, {required int rowSpan, required int columnSpan}) async {
    return await repository.resizeWidget(widgetId, rowSpan: rowSpan, columnSpan: columnSpan);
  }
}

// 搜索应用小部件用例
class SearchAppWidgetsUseCase {
  final DashboardRepository repository;

  SearchAppWidgetsUseCase({required this.repository});

  Future<Either<Failure, List<AppWidget>>> call(String query) async {
    return await repository.searchAppWidgets(query);
  }
} 