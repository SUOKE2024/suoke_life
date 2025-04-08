import 'package:dartz/dartz.dart';
import '../../core/network/network_info.dart';
import '../../core/utils/failure.dart';
import '../../domain/entities/app_dashboard.dart';
import '../../domain/repositories/dashboard_repository.dart';

class DashboardRepositoryImpl implements DashboardRepository {
  final DashboardRemoteDataSource remoteDataSource;
  final DashboardLocalDataSource localDataSource;
  final NetworkInfo? networkInfo;

  DashboardRepositoryImpl({
    required this.remoteDataSource,
    required this.localDataSource,
    this.networkInfo,
  });

  @override
  Future<Either<Failure, AppDashboard>> getUserDashboard() async {
    if (await networkInfo?.isConnected ?? true) {
      try {
        final remoteDashboard = await remoteDataSource.getUserDashboard();
        await localDataSource.cacheDashboard(remoteDashboard);
        return Right(remoteDashboard);
      } catch (e) {
        final cachedDashboard = await localDataSource.getCachedDashboard();
        if (cachedDashboard != null) {
          return Right(cachedDashboard);
        }
        return Left(CacheFailure(message: '缓存获取失败'));
      }
    } else {
      try {
        final cachedDashboard = await localDataSource.getCachedDashboard();
        if (cachedDashboard != null) {
          return Right(cachedDashboard);
        }
        return Left(CacheFailure(message: '网络连接不可用'));
      } catch (e) {
        return Left(CacheFailure(message: '缓存操作失败'));
      }
    }
  }

  @override
  Future<Either<Failure, AppDashboard>> updateDashboard(AppDashboard dashboard) async {
    if (await networkInfo?.isConnected ?? true) {
      try {
        final updatedDashboard = await remoteDataSource.updateDashboard(dashboard);
        await localDataSource.cacheDashboard(updatedDashboard);
        return Right(updatedDashboard);
      } catch (e) {
        return Left(ServerFailure(message: '更新仪表盘失败'));
      }
    } else {
      return Left(NetworkFailure(message: '网络连接不可用'));
    }
  }

  @override
  Future<Either<Failure, AppDashboard>> addWidget(AppWidget widget, {int row = 0, int column = 0}) async {
    if (await networkInfo?.isConnected ?? true) {
      try {
        final updatedDashboard = await remoteDataSource.addWidget(widget, row: row, column: column);
        await localDataSource.cacheDashboard(updatedDashboard);
        return Right(updatedDashboard);
      } catch (e) {
        return Left(ServerFailure(message: '服务器请求失败'));
      }
    } else {
      return Left(NetworkFailure(message: '网络连接不可用'));
    }
  }

  @override
  Future<Either<Failure, AppDashboard>> removeWidget(String widgetId) async {
    if (await networkInfo?.isConnected ?? true) {
      try {
        final updatedDashboard = await remoteDataSource.removeWidget(widgetId);
        await localDataSource.cacheDashboard(updatedDashboard);
        return Right(updatedDashboard);
      } catch (e) {
        return Left(ServerFailure(message: '服务器请求失败'));
      }
    } else {
      return Left(NetworkFailure(message: '网络连接不可用'));
    }
  }

  @override
  Future<Either<Failure, List<AppCategory>>> getAppCategories() async {
    if (await networkInfo?.isConnected ?? true) {
      try {
        final categories = await remoteDataSource.getAppCategories();
        await localDataSource.cacheCategories(categories);
        return Right(categories);
      } catch (e) {
        final cachedCategories = await localDataSource.getCachedCategories();
        if (cachedCategories != null) {
          return Right(cachedCategories);
        }
        return Left(ServerFailure(message: '服务器请求失败'));
      }
    } else {
      try {
        final cachedCategories = await localDataSource.getCachedCategories();
        if (cachedCategories != null) {
          return Right(cachedCategories);
        }
        return Left(CacheFailure(message: '缓存获取失败'));
      } catch (e) {
        return Left(CacheFailure(message: '缓存操作失败'));
      }
    }
  }

  @override
  Future<Either<Failure, List<AppWidget>>> getAppWidgetsByCategory(String categoryId) async {
    if (await networkInfo?.isConnected ?? true) {
      try {
        final widgets = await remoteDataSource.getAppWidgetsByCategory(categoryId);
        return Right(widgets);
      } catch (e) {
        return Left(ServerFailure(message: '获取分类组件失败'));
      }
    } else {
      return Left(NetworkFailure(message: '网络连接不可用'));
    }
  }

  @override
  Future<Either<Failure, AppDashboard>> moveWidgetPosition(String widgetId, {required int newRow, required int newColumn}) async {
    if (await networkInfo?.isConnected ?? true) {
      try {
        final updatedDashboard = await remoteDataSource.moveWidgetPosition(
          widgetId, 
          newRow: newRow, 
          newColumn: newColumn,
        );
        await localDataSource.cacheDashboard(updatedDashboard);
        return Right(updatedDashboard);
      } catch (e) {
        return Left(ServerFailure(message: '移动组件位置失败'));
      }
    } else {
      return Left(NetworkFailure(message: '网络连接不可用'));
    }
  }

  @override
  Future<Either<Failure, AppDashboard>> resizeWidget(String widgetId, {required int rowSpan, required int columnSpan}) async {
    if (await networkInfo?.isConnected ?? true) {
      try {
        final updatedDashboard = await remoteDataSource.resizeWidget(
          widgetId, 
          rowSpan: rowSpan, 
          columnSpan: columnSpan,
        );
        await localDataSource.cacheDashboard(updatedDashboard);
        return Right(updatedDashboard);
      } catch (e) {
        return Left(ServerFailure(message: '调整组件大小失败'));
      }
    } else {
      return Left(NetworkFailure(message: '网络连接不可用'));
    }
  }

  @override
  Future<Either<Failure, List<AppWidget>>> searchAppWidgets(String query) async {
    if (await networkInfo?.isConnected ?? true) {
      try {
        final widgets = await remoteDataSource.searchAppWidgets(query);
        return Right(widgets);
      } catch (e) {
        return Left(ServerFailure(message: '搜索组件失败'));
      }
    } else {
      return Left(NetworkFailure(message: '网络连接不可用'));
    }
  }

  @override
  Future<Either<Failure, AppDashboard>> resetDashboardToDefault() async {
    if (await networkInfo?.isConnected ?? true) {
      try {
        final defaultDashboard = await remoteDataSource.resetDashboardToDefault();
        await localDataSource.cacheDashboard(defaultDashboard);
        return Right(defaultDashboard);
      } catch (e) {
        return Left(ServerFailure(message: '重置仪表盘失败'));
      }
    } else {
      return Left(NetworkFailure(message: '网络连接不可用'));
    }
  }

  @override
  Future<Either<Failure, List<AppWidget>>> getRecommendedWidgets() async {
    if (await networkInfo?.isConnected ?? true) {
      try {
        final widgets = await remoteDataSource.getRecommendedWidgets();
        return Right(widgets);
      } catch (e) {
        return Left(ServerFailure(message: '获取推荐组件失败'));
      }
    } else {
      return Left(NetworkFailure(message: '网络连接不可用'));
    }
  }

  @override
  Future<Either<Failure, bool>> saveCustomLayout(String layoutName, AppDashboard dashboard) async {
    if (await networkInfo?.isConnected ?? true) {
      try {
        final result = await remoteDataSource.saveCustomLayout(layoutName, dashboard);
        // 如果保存成功，更新本地缓存的布局列表
        if (result) {
          final layouts = await remoteDataSource.getSavedLayouts();
          await localDataSource.cacheLayouts(layouts);
        }
        return Right(result);
      } catch (e) {
        return Left(ServerFailure(message: '保存自定义布局失败'));
      }
    } else {
      return Left(NetworkFailure(message: '网络连接不可用'));
    }
  }

  @override
  Future<Either<Failure, AppDashboard>> loadCustomLayout(String layoutId) async {
    if (await networkInfo?.isConnected ?? true) {
      try {
        final dashboard = await remoteDataSource.loadCustomLayout(layoutId);
        await localDataSource.cacheDashboard(dashboard);
        return Right(dashboard);
      } catch (e) {
        return Left(ServerFailure(message: '加载自定义布局失败'));
      }
    } else {
      return Left(NetworkFailure(message: '网络连接不可用'));
    }
  }

  @override
  Future<Either<Failure, List<SavedLayout>>> getSavedLayouts() async {
    if (await networkInfo?.isConnected ?? true) {
      try {
        final layouts = await remoteDataSource.getSavedLayouts();
        await localDataSource.cacheLayouts(layouts);
        return Right(layouts);
      } catch (e) {
        final cachedLayouts = await localDataSource.getCachedLayouts();
        if (cachedLayouts != null) {
          return Right(cachedLayouts);
        }
        return Left(ServerFailure(message: '获取保存的布局失败'));
      }
    } else {
      try {
        final cachedLayouts = await localDataSource.getCachedLayouts();
        if (cachedLayouts != null) {
          return Right(cachedLayouts);
        }
        return Left(NetworkFailure(message: '网络连接不可用'));
      } catch (e) {
        return Left(CacheFailure(message: '缓存获取失败'));
      }
    }
  }

  @override
  Future<Either<Failure, bool>> deleteCustomLayout(String layoutId) async {
    if (await networkInfo?.isConnected ?? true) {
      try {
        final result = await remoteDataSource.deleteCustomLayout(layoutId);
        // 如果删除成功，更新本地缓存的布局列表
        if (result) {
          final layouts = await remoteDataSource.getSavedLayouts();
          await localDataSource.cacheLayouts(layouts);
        }
        return Right(result);
      } catch (e) {
        return Left(ServerFailure(message: "服务器请求失败"));
      }
    } else {
      return Left(NetworkFailure(message: "网络连接不可用"));
    }
  }
} 