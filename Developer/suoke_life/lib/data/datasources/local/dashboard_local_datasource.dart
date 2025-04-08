import 'dart:convert';
import '../../../domain/entities/app_dashboard.dart';
import '../../../domain/repositories/dashboard_repository.dart';
import '../../models/dashboard_model.dart';
import '../../../core/database/database_service.dart';
import '../../../core/error/exceptions.dart';

class DashboardLocalDataSourceImpl implements DashboardLocalDataSource {
  final DatabaseService database;
  
  // 缓存相关常量
  static const String dashboardTable = 'dashboard_cache';
  static const String categoriesTable = 'dashboard_categories_cache';
  static const String layoutsTable = 'dashboard_layouts_cache';
  
  DashboardLocalDataSourceImpl({required this.database});

  @override
  Future<AppDashboard?> getCachedDashboard() async {
    try {
      final db = await database.database;
      final result = await db.query(
        dashboardTable,
        orderBy: 'updated_at DESC',
        limit: 1,
      );

      if (result.isNotEmpty) {
        final dashboardJson = json.decode(result.first['data'] as String);
        final dashboardModel = AppDashboardModel.fromJson(dashboardJson);
        return dashboardModel.toEntity();
      }
      
      return null;
    } catch (e) {
      throw CacheException();
    }
  }

  @override
  Future<void> cacheDashboard(AppDashboard dashboard) async {
    try {
      final db = await database.database;
      final dashboardModel = AppDashboardModel.fromEntity(dashboard);
      
      // 先清除旧缓存
      await db.delete(dashboardTable);
      
      // 插入新缓存
      await db.insert(
        dashboardTable,
        {
          'id': dashboard.id,
          'user_id': dashboard.userId,
          'data': json.encode(dashboardModel.toJson()),
          'updated_at': dashboard.updatedAt.toIso8601String(),
        },
      );
    } catch (e) {
      throw CacheException();
    }
  }

  @override
  Future<List<AppCategory>?> getCachedCategories() async {
    try {
      final db = await database.database;
      final result = await db.query(categoriesTable);

      if (result.isNotEmpty) {
        return result.map((row) {
          final categoryJson = json.decode(row['data'] as String);
          final categoryModel = AppCategoryModel.fromJson(categoryJson);
          return categoryModel.toEntity();
        }).toList();
      }
      
      return null;
    } catch (e) {
      throw CacheException();
    }
  }

  @override
  Future<void> cacheCategories(List<AppCategory> categories) async {
    try {
      final db = await database.database;
      
      // 开始事务
      await db.transaction((txn) async {
        // 删除旧数据
        await txn.delete(categoriesTable);
        
        // 插入新数据
        for (var category in categories) {
          final categoryModel = AppCategoryModel.fromEntity(category);
          await txn.insert(
            categoriesTable,
            {
              'id': category.id,
              'data': json.encode(categoryModel.toJson()),
              'updated_at': DateTime.now().toIso8601String(),
            },
          );
        }
      });
    } catch (e) {
      throw CacheException();
    }
  }

  @override
  Future<List<SavedLayout>?> getCachedLayouts() async {
    try {
      final db = await database.database;
      final result = await db.query(
        layoutsTable,
        orderBy: 'created_at DESC',
      );

      if (result.isNotEmpty) {
        return result.map((row) {
          final layoutJson = json.decode(row['data'] as String);
          final layoutModel = SavedLayoutModel.fromJson(layoutJson);
          return layoutModel.toEntity();
        }).toList();
      }
      
      return null;
    } catch (e) {
      throw CacheException();
    }
  }

  @override
  Future<void> cacheLayouts(List<SavedLayout> layouts) async {
    try {
      final db = await database.database;
      
      // 开始事务
      await db.transaction((txn) async {
        // 删除旧数据
        await txn.delete(layoutsTable);
        
        // 插入新数据
        for (var layout in layouts) {
          final layoutModel = SavedLayoutModel.fromEntity(layout);
          await txn.insert(
            layoutsTable,
            {
              'id': layout.id,
              'name': layout.name,
              'data': json.encode(layoutModel.toJson()),
              'created_at': layout.createdAt.toIso8601String(),
            },
          );
        }
      });
    } catch (e) {
      throw CacheException();
    }
  }

  @override
  Future<void> clearCache() async {
    try {
      final db = await database.database;
      
      await db.transaction((txn) async {
        await txn.delete(dashboardTable);
        await txn.delete(categoriesTable);
        await txn.delete(layoutsTable);
      });
    } catch (e) {
      throw CacheException();
    }
  }
  
  // 确保表存在
  Future<void> _ensureTablesExist() async {
    try {
      final db = await database.database;
      
      // 仪表盘缓存表
      await db.execute('''
        CREATE TABLE IF NOT EXISTS $dashboardTable (
          id TEXT PRIMARY KEY,
          user_id TEXT NOT NULL,
          data TEXT NOT NULL,
          updated_at TEXT NOT NULL
        )
      ''');
      
      // 应用分类缓存表
      await db.execute('''
        CREATE TABLE IF NOT EXISTS $categoriesTable (
          id TEXT PRIMARY KEY,
          data TEXT NOT NULL,
          updated_at TEXT NOT NULL
        )
      ''');
      
      // 布局缓存表
      await db.execute('''
        CREATE TABLE IF NOT EXISTS $layoutsTable (
          id TEXT PRIMARY KEY,
          name TEXT NOT NULL,
          data TEXT NOT NULL,
          created_at TEXT NOT NULL
        )
      ''');
    } catch (e) {
      throw CacheException();
    }
  }
  
  // 初始化表结构，应在应用启动时调用
  Future<void> initialize() async {
    await _ensureTablesExist();
  }
} 