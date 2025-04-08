import 'package:dio/dio.dart';
import '../../../domain/entities/app_dashboard.dart';
import '../../../domain/repositories/dashboard_repository.dart';
import '../../models/dashboard_model.dart';
import '../../../core/network/api_endpoints.dart';
import '../../../core/error/exceptions.dart';

class DashboardRemoteDataSourceImpl implements DashboardRemoteDataSource {
  final Dio dio;

  DashboardRemoteDataSourceImpl({required this.dio});

  @override
  Future<AppDashboard> getUserDashboard() async {
    try {
      final response = await dio.get(ApiEndpoints.dashboard);
      
      if (response.statusCode == 200) {
        final dashboardModel = AppDashboardModel.fromJson(response.data);
        return dashboardModel.toEntity();
      } else {
        throw ServerException();
      }
    } catch (e) {
      throw ServerException();
    }
  }

  @override
  Future<AppDashboard> updateDashboard(AppDashboard dashboard) async {
    try {
      final dashboardModel = AppDashboardModel.fromEntity(dashboard);
      final response = await dio.put(
        ApiEndpoints.dashboard,
        data: dashboardModel.toJson(),
      );
      
      if (response.statusCode == 200) {
        final updatedDashboardModel = AppDashboardModel.fromJson(response.data);
        return updatedDashboardModel.toEntity();
      } else {
        throw ServerException();
      }
    } catch (e) {
      throw ServerException();
    }
  }

  @override
  Future<AppDashboard> addWidget(AppWidget widget, {int row = 0, int column = 0}) async {
    try {
      final widgetModel = AppWidgetModel.fromEntity(widget);
      final response = await dio.post(
        ApiEndpoints.dashboardWidgets,
        data: {
          'widget': widgetModel.toJson(),
          'row': row,
          'column': column,
        },
      );
      
      if (response.statusCode == 200) {
        final updatedDashboardModel = AppDashboardModel.fromJson(response.data);
        return updatedDashboardModel.toEntity();
      } else {
        throw ServerException();
      }
    } catch (e) {
      throw ServerException();
    }
  }

  @override
  Future<AppDashboard> removeWidget(String widgetId) async {
    try {
      final response = await dio.delete(
        '${ApiEndpoints.dashboardWidgets}/$widgetId',
      );
      
      if (response.statusCode == 200) {
        final updatedDashboardModel = AppDashboardModel.fromJson(response.data);
        return updatedDashboardModel.toEntity();
      } else {
        throw ServerException();
      }
    } catch (e) {
      throw ServerException();
    }
  }

  @override
  Future<List<AppCategory>> getAppCategories() async {
    try {
      final response = await dio.get(ApiEndpoints.appCategories);
      
      if (response.statusCode == 200) {
        final categoriesData = response.data as List;
        final categories = categoriesData
            .map((json) => AppCategoryModel.fromJson(json).toEntity())
            .toList();
        return categories;
      } else {
        throw ServerException();
      }
    } catch (e) {
      throw ServerException();
    }
  }

  @override
  Future<List<AppWidget>> getAppWidgetsByCategory(String categoryId) async {
    try {
      final response = await dio.get(
        '${ApiEndpoints.appWidgets}?categoryId=$categoryId',
      );
      
      if (response.statusCode == 200) {
        final widgetsData = response.data as List;
        final widgets = widgetsData
            .map((json) => AppWidgetModel.fromJson(json).toEntity())
            .toList();
        return widgets;
      } else {
        throw ServerException();
      }
    } catch (e) {
      throw ServerException();
    }
  }

  @override
  Future<AppDashboard> moveWidgetPosition(String widgetId, {required int newRow, required int newColumn}) async {
    try {
      final response = await dio.put(
        '${ApiEndpoints.dashboardWidgets}/$widgetId/position',
        data: {
          'row': newRow,
          'column': newColumn,
        },
      );
      
      if (response.statusCode == 200) {
        final updatedDashboardModel = AppDashboardModel.fromJson(response.data);
        return updatedDashboardModel.toEntity();
      } else {
        throw ServerException();
      }
    } catch (e) {
      throw ServerException();
    }
  }

  @override
  Future<AppDashboard> resizeWidget(String widgetId, {required int rowSpan, required int columnSpan}) async {
    try {
      final response = await dio.put(
        '${ApiEndpoints.dashboardWidgets}/$widgetId/size',
        data: {
          'rowSpan': rowSpan,
          'columnSpan': columnSpan,
        },
      );
      
      if (response.statusCode == 200) {
        final updatedDashboardModel = AppDashboardModel.fromJson(response.data);
        return updatedDashboardModel.toEntity();
      } else {
        throw ServerException();
      }
    } catch (e) {
      throw ServerException();
    }
  }

  @override
  Future<List<AppWidget>> searchAppWidgets(String query) async {
    try {
      final response = await dio.get(
        '${ApiEndpoints.appWidgets}/search?q=$query',
      );
      
      if (response.statusCode == 200) {
        final widgetsData = response.data as List;
        final widgets = widgetsData
            .map((json) => AppWidgetModel.fromJson(json).toEntity())
            .toList();
        return widgets;
      } else {
        throw ServerException();
      }
    } catch (e) {
      throw ServerException();
    }
  }

  @override
  Future<AppDashboard> resetDashboardToDefault() async {
    try {
      final response = await dio.post(ApiEndpoints.dashboardReset);
      
      if (response.statusCode == 200) {
        final defaultDashboardModel = AppDashboardModel.fromJson(response.data);
        return defaultDashboardModel.toEntity();
      } else {
        throw ServerException();
      }
    } catch (e) {
      throw ServerException();
    }
  }

  @override
  Future<List<AppWidget>> getRecommendedWidgets() async {
    try {
      final response = await dio.get(ApiEndpoints.recommendedWidgets);
      
      if (response.statusCode == 200) {
        final widgetsData = response.data as List;
        final widgets = widgetsData
            .map((json) => AppWidgetModel.fromJson(json).toEntity())
            .toList();
        return widgets;
      } else {
        throw ServerException();
      }
    } catch (e) {
      throw ServerException();
    }
  }

  @override
  Future<bool> saveCustomLayout(String layoutName, AppDashboard dashboard) async {
    try {
      final dashboardModel = AppDashboardModel.fromEntity(dashboard);
      final response = await dio.post(
        ApiEndpoints.dashboardLayouts,
        data: {
          'name': layoutName,
          'dashboard': dashboardModel.toJson(),
        },
      );
      
      return response.statusCode == 200 || response.statusCode == 201;
    } catch (e) {
      throw ServerException();
    }
  }

  @override
  Future<AppDashboard> loadCustomLayout(String layoutId) async {
    try {
      final response = await dio.post(
        '${ApiEndpoints.dashboardLayouts}/$layoutId/load',
      );
      
      if (response.statusCode == 200) {
        final dashboardModel = AppDashboardModel.fromJson(response.data);
        return dashboardModel.toEntity();
      } else {
        throw ServerException();
      }
    } catch (e) {
      throw ServerException();
    }
  }

  @override
  Future<List<SavedLayout>> getSavedLayouts() async {
    try {
      final response = await dio.get(ApiEndpoints.dashboardLayouts);
      
      if (response.statusCode == 200) {
        final layoutsData = response.data as List;
        final layouts = layoutsData
            .map((json) => SavedLayoutModel.fromJson(json).toEntity())
            .toList();
        return layouts;
      } else {
        throw ServerException();
      }
    } catch (e) {
      throw ServerException();
    }
  }

  @override
  Future<bool> deleteCustomLayout(String layoutId) async {
    try {
      final response = await dio.delete(
        '${ApiEndpoints.dashboardLayouts}/$layoutId',
      );
      
      return response.statusCode == 200 || response.statusCode == 204;
    } catch (e) {
      throw ServerException();
    }
  }
} 