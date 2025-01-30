import 'dart:convert';
import 'package:logger/logger.dart';
import '../../models/health_data.dart';
import '../../local/dao/health_data_dao.dart';
import '../interfaces/health_data_repository.dart';
import 'base_repository_impl.dart';

/// 健康数据仓库实现
class HealthDataRepositoryImpl extends BaseRepositoryImpl<HealthData>
    implements HealthDataRepository {
  final HealthDataDao _dao;
  final Logger _logger = Logger();

  HealthDataRepositoryImpl(this._dao) : super(_dao);

  @override
  Future<List<HealthData>> getUserHealthData(String userId) async {
    try {
      return await _dao.findByUserId(userId);
    } catch (e) {
      _logger.e('Error getting user health data: $e');
      rethrow;
    }
  }

  @override
  Future<List<HealthData>> getUserHealthDataByType(String userId, String type) async {
    try {
      return await _dao.findByUserIdAndType(userId, type);
    } catch (e) {
      _logger.e('Error getting user health data by type: $e');
      rethrow;
    }
  }

  @override
  Future<List<HealthData>> getHealthDataByTimeRange(int startTime, int endTime) async {
    try {
      return await _dao.findByTimeRange(startTime, endTime);
    } catch (e) {
      _logger.e('Error getting health data by time range: $e');
      rethrow;
    }
  }

  @override
  Future<List<HealthData>> getUserHealthDataByTypeAndTime(
    String userId,
    String type,
    int startTime,
    int endTime,
  ) async {
    try {
      return await _dao.findByUserIdTypeAndTimeRange(userId, type, startTime, endTime);
    } catch (e) {
      _logger.e('Error getting user health data by type and time: $e');
      rethrow;
    }
  }

  @override
  Future<HealthData?> getLatestHealthData(String userId, String type) async {
    try {
      return await _dao.findLatest(userId, type);
    } catch (e) {
      _logger.e('Error getting latest health data: $e');
      rethrow;
    }
  }

  @override
  Future<List<String>> getUserHealthDataTypes(String userId) async {
    try {
      return await _dao.getUserDataTypes(userId);
    } catch (e) {
      _logger.e('Error getting user health data types: $e');
      rethrow;
    }
  }

  @override
  Future<List<String>> getHealthDataSources() async {
    try {
      return await _dao.getDataSources();
    } catch (e) {
      _logger.e('Error getting health data sources: $e');
      rethrow;
    }
  }

  @override
  Future<Map<String, dynamic>> getHealthDataStats(
    String userId,
    String type,
    int startTime,
    int endTime,
  ) async {
    try {
      final stats = <String, dynamic>{};
      
      // 获取基本统计数据
      stats['average'] = await _dao.getAverageValue(userId, type, startTime, endTime);
      stats['max'] = await _dao.getMaxValue(userId, type, startTime, endTime);
      stats['min'] = await _dao.getMinValue(userId, type, startTime, endTime);
      
      // 获取数据点数量
      final data = await getUserHealthDataByTypeAndTime(userId, type, startTime, endTime);
      stats['count'] = data.length;
      
      // 获取最新值
      final latest = await getLatestHealthData(userId, type);
      stats['latest'] = latest?.value;
      
      return stats;
    } catch (e) {
      _logger.e('Error getting health data stats: $e');
      rethrow;
    }
  }

  @override
  Future<void> saveHealthDataList(List<HealthData> dataList) async {
    try {
      await _dao.saveAll(dataList);
    } catch (e) {
      _logger.e('Error saving health data list: $e');
      rethrow;
    }
  }

  @override
  Future<void> deleteUserHealthData(String userId) async {
    try {
      await _dao.deleteByUserId(userId);
    } catch (e) {
      _logger.e('Error deleting user health data: $e');
      rethrow;
    }
  }

  @override
  Future<void> deleteHealthDataByType(String userId, String type) async {
    try {
      await _dao.deleteByType(userId, type);
    } catch (e) {
      _logger.e('Error deleting health data by type: $e');
      rethrow;
    }
  }

  @override
  Future<void> clearAllHealthData() async {
    try {
      await _dao.clear();
    } catch (e) {
      _logger.e('Error clearing all health data: $e');
      rethrow;
    }
  }

  @override
  Future<String> exportHealthData(String userId, String format) async {
    try {
      final data = await getUserHealthData(userId);
      
      switch (format.toLowerCase()) {
        case 'json':
          return json.encode(data.map((d) => d.toMap()).toList());
        case 'csv':
          final header = 'Type,Value,Unit,Time,Source,Notes\n';
          final rows = data.map((d) => 
            '${d.type},${d.value},${d.unit},${d.time},${d.source},${d.notes ?? ""}'
          ).join('\n');
          return header + rows;
        default:
          throw ArgumentError('Unsupported format: $format');
      }
    } catch (e) {
      _logger.e('Error exporting health data: $e');
      rethrow;
    }
  }

  @override
  Future<void> importHealthData(String data, String format) async {
    try {
      List<HealthData> healthDataList;
      
      switch (format.toLowerCase()) {
        case 'json':
          final List<dynamic> jsonData = json.decode(data);
          healthDataList = jsonData.map((d) => HealthData.fromMap(d)).toList();
          break;
        default:
          throw ArgumentError('Unsupported format: $format');
      }
      
      await saveHealthDataList(healthDataList);
    } catch (e) {
      _logger.e('Error importing health data: $e');
      rethrow;
    }
  }

  @override
  Future<Map<String, dynamic>> getHealthDataTrend(
    String userId,
    String type,
    int startTime,
    int endTime,
    String interval,
  ) async {
    try {
      final data = await getUserHealthDataByTypeAndTime(userId, type, startTime, endTime);
      final trend = <String, dynamic>{
        'data_points': data.length,
        'interval': interval,
        'values': <String, double>{},
      };
      
      // 根据间隔计算趋势
      for (var item in data) {
        final date = DateTime.fromMillisecondsSinceEpoch(item.time);
        String key;
        
        switch (interval.toLowerCase()) {
          case 'hour':
            key = '${date.year}-${date.month}-${date.day}-${date.hour}';
            break;
          case 'day':
            key = '${date.year}-${date.month}-${date.day}';
            break;
          case 'week':
            final weekNumber = (date.day + date.weekday - 1) ~/ 7 + 1;
            key = '${date.year}-${date.month}-W$weekNumber';
            break;
          case 'month':
            key = '${date.year}-${date.month}';
            break;
          default:
            throw ArgumentError('Unsupported interval: $interval');
        }
        
        trend['values'][key] = (trend['values'][key] ?? 0.0) + item.value;
      }
      
      return trend;
    } catch (e) {
      _logger.e('Error getting health data trend: $e');
      rethrow;
    }
  }

  @override
  Future<bool> isHealthDataNormal(String type, double value) async {
    try {
      final ranges = HealthData.healthDataRanges[type];
      if (ranges == null) return true;
      
      return value >= ranges['min']! && value <= ranges['max']!;
    } catch (e) {
      _logger.e('Error checking if health data is normal: $e');
      rethrow;
    }
  }

  @override
  Future<List<HealthData>> getAbnormalHealthData(
    String userId,
    String type,
    int startTime,
    int endTime,
  ) async {
    try {
      final data = await getUserHealthDataByTypeAndTime(userId, type, startTime, endTime);
      final ranges = HealthData.healthDataRanges[type];
      
      if (ranges == null) return [];
      
      return data.where((item) => 
        item.value < ranges['min']! || item.value > ranges['max']!
      ).toList();
    } catch (e) {
      _logger.e('Error getting abnormal health data: $e');
      rethrow;
    }
  }

  @override
  Future<void> syncExternalHealthData(String source, String userId) async {
    try {
      // TODO: 实现与外部健康数据源的同步
      // 这里需要根据具体的外部数据源实现同步逻辑
      throw UnimplementedError('External health data sync not implemented for source: $source');
    } catch (e) {
      _logger.e('Error syncing external health data: $e');
      rethrow;
    }
  }
} 