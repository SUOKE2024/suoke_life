import 'dart:convert';

import 'package:logger/logger.dart';
import 'package:sqflite/sqflite.dart';

import '../../../domain/entities/health_data.dart';
import '../../models/health_data_model.dart';
import '../health_data_source.dart';
import 'database_helper.dart';

/// 健康数据本地数据源实现
/// 负责在本地数据库中存储和管理健康数据
class HealthDataLocalSource implements HealthDataSource {
  final DatabaseHelper _databaseHelper;
  final Logger _logger;
  
  // 健康数据表名
  static const String _tableHealthData = 'health_data';
  
  HealthDataLocalSource({
    required DatabaseHelper databaseHelper,
    required Logger logger,
  })  : _databaseHelper = databaseHelper,
        _logger = logger;
  
  @override
  Future<List<HealthDataModel>> getUserHealthData(
    String userId, {
    DateTime? startDate,
    DateTime? endDate,
    int limit = 100,
    int offset = 0,
  }) async {
    try {
      final db = await _databaseHelper.database;
      
      // 构建查询条件
      final List<String> whereConditions = ['user_id = ?'];
      final List<dynamic> whereArgs = [userId];
      
      if (startDate != null) {
        whereConditions.add('timestamp >= ?');
        whereArgs.add(startDate.millisecondsSinceEpoch);
      }
      
      if (endDate != null) {
        whereConditions.add('timestamp <= ?');
        whereArgs.add(endDate.millisecondsSinceEpoch);
      }
      
      final String whereClause = whereConditions.join(' AND ');
      
      // 执行查询
      final List<Map<String, dynamic>> maps = await db.query(
        _tableHealthData,
        where: whereClause,
        whereArgs: whereArgs,
        orderBy: 'timestamp DESC',
        limit: limit,
        offset: offset,
      );
      
      // 转换查询结果为模型对象
      return maps.map((map) {
        // 处理JSON字段
        final Map<String, dynamic> processedMap = {...map};
        if (processedMap['metadata'] != null && processedMap['metadata'] is String) {
          processedMap['metadata'] = jsonDecode(processedMap['metadata'] as String);
        }
        
        return HealthDataModel.fromJson(processedMap);
      }).toList();
    } catch (e) {
      _logger.e('获取用户健康数据失败: $e');
      throw Exception('获取用户健康数据失败: $e');
    }
  }
  
  @override
  Future<List<HealthDataModel>> getHealthDataByType(
    String userId,
    HealthDataType type, {
    DateTime? startDate,
    DateTime? endDate,
    int limit = 100,
    int offset = 0,
  }) async {
    try {
      final db = await _databaseHelper.database;
      
      // 构建查询条件
      final List<String> whereConditions = ['user_id = ?', 'type = ?'];
      final List<dynamic> whereArgs = [userId, type.toString()];
      
      if (startDate != null) {
        whereConditions.add('timestamp >= ?');
        whereArgs.add(startDate.millisecondsSinceEpoch);
      }
      
      if (endDate != null) {
        whereConditions.add('timestamp <= ?');
        whereArgs.add(endDate.millisecondsSinceEpoch);
      }
      
      final String whereClause = whereConditions.join(' AND ');
      
      // 执行查询
      final List<Map<String, dynamic>> maps = await db.query(
        _tableHealthData,
        where: whereClause,
        whereArgs: whereArgs,
        orderBy: 'timestamp DESC',
        limit: limit,
        offset: offset,
      );
      
      // 转换查询结果为模型对象
      return maps.map((map) {
        // 处理JSON字段
        final Map<String, dynamic> processedMap = {...map};
        if (processedMap['metadata'] != null && processedMap['metadata'] is String) {
          processedMap['metadata'] = jsonDecode(processedMap['metadata'] as String);
        }
        
        return HealthDataModel.fromJson(processedMap);
      }).toList();
    } catch (e) {
      _logger.e('获取用户特定类型健康数据失败: $e');
      throw Exception('获取用户特定类型健康数据失败: $e');
    }
  }
  
  @override
  Future<HealthDataModel> getHealthDataById(String dataId) async {
    try {
      final db = await _databaseHelper.database;
      
      // 执行查询
      final List<Map<String, dynamic>> maps = await db.query(
        _tableHealthData,
        where: 'id = ?',
        whereArgs: [dataId],
        limit: 1,
      );
      
      if (maps.isEmpty) {
        throw Exception('未找到ID为 $dataId 的健康数据');
      }
      
      // 处理JSON字段
      final Map<String, dynamic> processedMap = {...maps.first};
      if (processedMap['metadata'] != null && processedMap['metadata'] is String) {
        processedMap['metadata'] = jsonDecode(processedMap['metadata'] as String);
      }
      
      return HealthDataModel.fromJson(processedMap);
    } catch (e) {
      _logger.e('获取健康数据详情失败: $e');
      throw Exception('获取健康数据详情失败: $e');
    }
  }
  
  @override
  Future<HealthDataModel> saveHealthData(HealthDataModel data) async {
    try {
      final db = await _databaseHelper.database;
      
      // 准备数据
      final Map<String, dynamic> dataMap = data.toJson();
      
      // 处理JSON字段
      if (dataMap['metadata'] != null) {
        dataMap['metadata'] = jsonEncode(dataMap['metadata']);
      }
      
      // 插入数据
      await db.insert(
        _tableHealthData,
        dataMap,
        conflictAlgorithm: ConflictAlgorithm.replace,
      );
      
      return data;
    } catch (e) {
      _logger.e('保存健康数据失败: $e');
      throw Exception('保存健康数据失败: $e');
    }
  }
  
  @override
  Future<List<HealthDataModel>> saveBatchHealthData(List<HealthDataModel> dataList) async {
    try {
      final db = await _databaseHelper.database;
      
      // 开始事务
      await db.transaction((txn) async {
        for (final data in dataList) {
          // 准备数据
          final Map<String, dynamic> dataMap = data.toJson();
          
          // 处理JSON字段
          if (dataMap['metadata'] != null) {
            dataMap['metadata'] = jsonEncode(dataMap['metadata']);
          }
          
          // 插入数据
          await txn.insert(
            _tableHealthData,
            dataMap,
            conflictAlgorithm: ConflictAlgorithm.replace,
          );
        }
      });
      
      return dataList;
    } catch (e) {
      _logger.e('批量保存健康数据失败: $e');
      throw Exception('批量保存健康数据失败: $e');
    }
  }
  
  @override
  Future<HealthDataModel> updateHealthData(HealthDataModel data) async {
    try {
      final db = await _databaseHelper.database;
      
      // 准备数据
      final Map<String, dynamic> dataMap = data.toJson();
      
      // 处理JSON字段
      if (dataMap['metadata'] != null) {
        dataMap['metadata'] = jsonEncode(dataMap['metadata']);
      }
      
      // 更新数据
      await db.update(
        _tableHealthData,
        dataMap,
        where: 'id = ?',
        whereArgs: [data.id],
      );
      
      return data;
    } catch (e) {
      _logger.e('更新健康数据失败: $e');
      throw Exception('更新健康数据失败: $e');
    }
  }
  
  @override
  Future<void> deleteHealthData(String dataId) async {
    try {
      final db = await _databaseHelper.database;
      
      // 删除数据
      await db.delete(
        _tableHealthData,
        where: 'id = ?',
        whereArgs: [dataId],
      );
    } catch (e) {
      _logger.e('删除健康数据失败: $e');
      throw Exception('删除健康数据失败: $e');
    }
  }
  
  @override
  Future<void> deleteBatchHealthData(List<String> dataIds) async {
    try {
      final db = await _databaseHelper.database;
      
      // 开始事务
      await db.transaction((txn) async {
        for (final id in dataIds) {
          // 删除数据
          await txn.delete(
            _tableHealthData,
            where: 'id = ?',
            whereArgs: [id],
          );
        }
      });
    } catch (e) {
      _logger.e('批量删除健康数据失败: $e');
      throw Exception('批量删除健康数据失败: $e');
    }
  }
  
  @override
  Future<Map<HealthDataType, num>> getDailyHealthSummary(
    String userId,
    DateTime date,
  ) async {
    try {
      final db = await _databaseHelper.database;
      
      // 计算日期范围
      final startOfDay = DateTime(date.year, date.month, date.day);
      final endOfDay = DateTime(date.year, date.month, date.day, 23, 59, 59, 999);
      
      // 获取当天的所有健康数据
      final List<Map<String, dynamic>> maps = await db.query(
        _tableHealthData,
        where: 'user_id = ? AND timestamp >= ? AND timestamp <= ?',
        whereArgs: [
          userId,
          startOfDay.millisecondsSinceEpoch,
          endOfDay.millisecondsSinceEpoch,
        ],
      );
      
      // 按类型分组并计算汇总值
      final Map<HealthDataType, num> summary = {};
      
      for (final map in maps) {
        // 处理JSON字段
        final Map<String, dynamic> processedMap = {...map};
        if (processedMap['metadata'] != null && processedMap['metadata'] is String) {
          processedMap['metadata'] = jsonDecode(processedMap['metadata'] as String);
        }
        
        final healthData = HealthDataModel.fromJson(processedMap);
        final type = healthData.type;
        
        // 根据数据类型进行不同的汇总计算
        if (summary.containsKey(type)) {
          // 对于步数、水分摄入等累加型数据，直接累加
          if (type == HealthDataType.steps || 
              type == HealthDataType.waterIntake ||
              type == HealthDataType.activity) {
            summary[type] = summary[type]! + healthData.value;
          } 
          // 对于心率、血压等测量型数据，取平均值
          else if (type == HealthDataType.heartRate || 
                   type == HealthDataType.bloodPressure ||
                   type == HealthDataType.bloodOxygen ||
                   type == HealthDataType.temperature) {
            // 这里简化处理，实际应用中可能需要更复杂的逻辑
            summary[type] = (summary[type]! + healthData.value) / 2;
          }
          // 对于睡眠等时长型数据，累加时长
          else if (type == HealthDataType.sleep) {
            summary[type] = summary[type]! + healthData.value;
          }
          // 其他类型数据，取最新值
          else {
            // 比较时间戳，保留最新的数据
            final existingData = maps.firstWhere(
              (m) => m['type'] == type.toString() && 
                     summary[type] == HealthDataModel.fromJson(m).value,
            );
            
            final existingTimestamp = existingData['timestamp'] as int;
            final newTimestamp = healthData.timestamp.millisecondsSinceEpoch;
            
            if (newTimestamp > existingTimestamp) {
              summary[type] = healthData.value;
            }
          }
        } else {
          summary[type] = healthData.value;
        }
      }
      
      return summary;
    } catch (e) {
      _logger.e('获取每日健康数据汇总失败: $e');
      throw Exception('获取每日健康数据汇总失败: $e');
    }
  }
  
  @override
  Future<Map<String, dynamic>> getHealthStatistics(
    String userId,
    HealthDataType type, {
    required DateTime startDate,
    required DateTime endDate,
    String? groupBy,
  }) async {
    try {
      final db = await _databaseHelper.database;
      
      // 构建查询条件
      final whereConditions = 'user_id = ? AND type = ? AND timestamp >= ? AND timestamp <= ?';
      final whereArgs = [
        userId,
        type.toString(),
        startDate.millisecondsSinceEpoch,
        endDate.millisecondsSinceEpoch,
      ];
      
      // 执行查询
      final List<Map<String, dynamic>> maps = await db.query(
        _tableHealthData,
        where: whereConditions,
        whereArgs: whereArgs,
        orderBy: 'timestamp ASC',
      );
      
      // 转换查询结果为模型对象
      final dataList = maps.map((map) {
        // 处理JSON字段
        final Map<String, dynamic> processedMap = {...map};
        if (processedMap['metadata'] != null && processedMap['metadata'] is String) {
          processedMap['metadata'] = jsonDecode(processedMap['metadata'] as String);
        }
        
        return HealthDataModel.fromJson(processedMap);
      }).toList();
      
      // 计算统计数据
      if (dataList.isEmpty) {
        return {
          'count': 0,
          'min': 0,
          'max': 0,
          'avg': 0,
          'sum': 0,
          'first': null,
          'last': null,
          'data': [],
        };
      }
      
      // 基本统计
      final values = dataList.map((data) => data.value).toList();
      final min = values.reduce((a, b) => a < b ? a : b);
      final max = values.reduce((a, b) => a > b ? a : b);
      final sum = values.reduce((a, b) => a + b);
      final avg = sum / values.length;
      
      // 按时间分组
      final groupedData = <String, List<HealthDataModel>>{};
      
      if (groupBy != null) {
        for (final data in dataList) {
          final timestamp = data.timestamp;
          String key;
          
          switch (groupBy) {
            case 'hour':
              key = '${timestamp.year}-${timestamp.month.toString().padLeft(2, '0')}-${timestamp.day.toString().padLeft(2, '0')} ${timestamp.hour.toString().padLeft(2, '0')}:00';
              break;
            case 'day':
              key = '${timestamp.year}-${timestamp.month.toString().padLeft(2, '0')}-${timestamp.day.toString().padLeft(2, '0')}';
              break;
            case 'week':
              // 计算周的第一天（周一）
              final firstDayOfWeek = timestamp.subtract(Duration(days: timestamp.weekday - 1));
              key = '${firstDayOfWeek.year}-${firstDayOfWeek.month.toString().padLeft(2, '0')}-${firstDayOfWeek.day.toString().padLeft(2, '0')}';
              break;
            case 'month':
              key = '${timestamp.year}-${timestamp.month.toString().padLeft(2, '0')}';
              break;
            default:
              key = timestamp.toIso8601String();
          }
          
          if (!groupedData.containsKey(key)) {
            groupedData[key] = [];
          }
          
          groupedData[key]!.add(data);
        }
      }
      
      // 计算分组统计
      final groupStats = groupedData.map((key, dataList) {
        final values = dataList.map((data) => data.value).toList();
        final min = values.reduce((a, b) => a < b ? a : b);
        final max = values.reduce((a, b) => a > b ? a : b);
        final sum = values.reduce((a, b) => a + b);
        final avg = sum / values.length;
        
        return MapEntry(key, {
          'count': dataList.length,
          'min': min,
          'max': max,
          'avg': avg,
          'sum': sum,
          'first': dataList.first.toJson(),
          'last': dataList.last.toJson(),
        });
      });
      
      return {
        'count': dataList.length,
        'min': min,
        'max': max,
        'avg': avg,
        'sum': sum,
        'first': dataList.first.toJson(),
        'last': dataList.last.toJson(),
        'grouped': groupStats,
        'data': dataList.map((data) => data.toJson()).toList(),
      };
    } catch (e) {
      _logger.e('获取健康数据统计失败: $e');
      throw Exception('获取健康数据统计失败: $e');
    }
  }
  
  @override
  Future<HealthDataModel?> getLatestHealthData(
    String userId,
    HealthDataType type,
  ) async {
    try {
      final db = await _databaseHelper.database;
      
      // 执行查询
      final List<Map<String, dynamic>> maps = await db.query(
        _tableHealthData,
        where: 'user_id = ? AND type = ?',
        whereArgs: [userId, type.toString()],
        orderBy: 'timestamp DESC',
        limit: 1,
      );
      
      if (maps.isEmpty) {
        return null;
      }
      
      // 处理JSON字段
      final Map<String, dynamic> processedMap = {...maps.first};
      if (processedMap['metadata'] != null && processedMap['metadata'] is String) {
        processedMap['metadata'] = jsonDecode(processedMap['metadata'] as String);
      }
      
      return HealthDataModel.fromJson(processedMap);
    } catch (e) {
      _logger.e('获取最新健康数据失败: $e');
      throw Exception('获取最新健康数据失败: $e');
    }
  }
  
  @override
  Future<List<Map<String, dynamic>>> getHealthTrend(
    String userId,
    HealthDataType type, {
    required DateTime startDate,
    required DateTime endDate,
    required String interval,
  }) async {
    try {
      // 获取原始数据
      final statistics = await getHealthStatistics(
        userId,
        type,
        startDate: startDate,
        endDate: endDate,
        groupBy: interval,
      );
      
      // 提取分组数据
      final grouped = statistics['grouped'] as Map<String, dynamic>? ?? {};
      
      // 转换为趋势数据
      final trendData = grouped.entries.map((entry) {
        final date = entry.key;
        final stats = entry.value as Map<String, dynamic>;
        
        return {
          'date': date,
          'value': stats['avg'],
          'min': stats['min'],
          'max': stats['max'],
          'count': stats['count'],
        };
      }).toList();
      
      // 按日期排序
      trendData.sort((a, b) => (a['date'] as String).compareTo(b['date'] as String));
      
      return trendData;
    } catch (e) {
      _logger.e('获取健康数据趋势失败: $e');
      throw Exception('获取健康数据趋势失败: $e');
    }
  }
  
  @override
  Future<List<HealthDataModel>> syncExternalHealthData(
    String userId,
    String source, {
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    // 本地数据源不支持同步外部数据
    throw UnimplementedError('本地数据源不支持同步外部健康数据');
  }
} 