import 'dart:convert';
import 'package:logger/logger.dart';
import '../../models/life_record.dart';
import '../../local/dao/life_record_dao.dart';
import '../interfaces/life_record_repository.dart';
import 'base_repository_impl.dart';

/// 生活记录仓库实现
class LifeRecordRepositoryImpl extends BaseRepositoryImpl<LifeRecord>
    implements LifeRecordRepository {
  final LifeRecordDao _dao;
  final Logger _logger = Logger();

  LifeRecordRepositoryImpl(this._dao) : super(_dao);

  @override
  Future<List<LifeRecord>> getUserRecords(String userId) async {
    try {
      return await _dao.findByUserId(userId);
    } catch (e) {
      _logger.e('Error getting user records: $e');
      rethrow;
    }
  }

  @override
  Future<List<LifeRecord>> getRecordsByCategory(String category) async {
    try {
      return await _dao.findByCategory(category);
    } catch (e) {
      _logger.e('Error getting records by category: $e');
      rethrow;
    }
  }

  @override
  Future<List<LifeRecord>> getRecordsByTag(String tag) async {
    try {
      return await _dao.findByTag(tag);
    } catch (e) {
      _logger.e('Error getting records by tag: $e');
      rethrow;
    }
  }

  @override
  Future<List<LifeRecord>> getRecordsByTimeRange(String startTime, String endTime) async {
    try {
      return await _dao.findByTimeRange(startTime, endTime);
    } catch (e) {
      _logger.e('Error getting records by time range: $e');
      rethrow;
    }
  }

  @override
  Future<List<LifeRecord>> getRecordsByLocation(String location) async {
    try {
      return await _dao.findByLocation(location);
    } catch (e) {
      _logger.e('Error getting records by location: $e');
      rethrow;
    }
  }

  @override
  Future<List<LifeRecord>> searchRecords(String keyword) async {
    try {
      return await _dao.search(keyword);
    } catch (e) {
      _logger.e('Error searching records: $e');
      rethrow;
    }
  }

  @override
  Future<List<String>> getAvailableCategories() async {
    try {
      return await _dao.getAllCategories();
    } catch (e) {
      _logger.e('Error getting available categories: $e');
      rethrow;
    }
  }

  @override
  Future<List<String>> getUsedTags() async {
    try {
      return await _dao.getAllTags();
    } catch (e) {
      _logger.e('Error getting used tags: $e');
      rethrow;
    }
  }

  @override
  Future<List<String>> getRecordedLocations() async {
    try {
      return await _dao.getAllLocations();
    } catch (e) {
      _logger.e('Error getting recorded locations: $e');
      rethrow;
    }
  }

  @override
  Future<Map<String, int>> getUserStats(String userId) async {
    try {
      final records = await getUserRecords(userId);
      final stats = <String, int>{
        'total': records.length,
      };

      // 添加分类统计
      final categoryStats = await getCategoryStats(userId);
      stats.addAll(categoryStats);

      // 添加标签统计
      final tagStats = await getTagStats(userId);
      stats.addAll(tagStats);

      return stats;
    } catch (e) {
      _logger.e('Error getting user stats: $e');
      rethrow;
    }
  }

  @override
  Future<void> saveRecords(List<LifeRecord> records) async {
    try {
      await _dao.saveAll(records);
    } catch (e) {
      _logger.e('Error saving records: $e');
      rethrow;
    }
  }

  @override
  Future<void> deleteUserRecords(String userId) async {
    try {
      await _dao.deleteByUserId(userId);
    } catch (e) {
      _logger.e('Error deleting user records: $e');
      rethrow;
    }
  }

  @override
  Future<void> clearAllRecords() async {
    try {
      await _dao.clear();
    } catch (e) {
      _logger.e('Error clearing all records: $e');
      rethrow;
    }
  }

  @override
  Future<String> exportUserRecords(String userId, String format) async {
    try {
      final records = await getUserRecords(userId);
      
      switch (format.toLowerCase()) {
        case 'json':
          return json.encode(records.map((r) => r.toMap()).toList());
        case 'text':
          return records.map((r) => 
            '${r.timestamp} - ${r.category} - ${r.title}\n${r.content}'
          ).join('\n\n');
        default:
          throw ArgumentError('Unsupported format: $format');
      }
    } catch (e) {
      _logger.e('Error exporting user records: $e');
      rethrow;
    }
  }

  @override
  Future<void> importRecords(String data, String format) async {
    try {
      List<LifeRecord> records;
      
      switch (format.toLowerCase()) {
        case 'json':
          final List<dynamic> jsonData = json.decode(data);
          records = jsonData.map((r) => LifeRecord.fromMap(r)).toList();
          break;
        default:
          throw ArgumentError('Unsupported format: $format');
      }
      
      await saveRecords(records);
    } catch (e) {
      _logger.e('Error importing records: $e');
      rethrow;
    }
  }

  @override
  Future<Map<String, int>> getTagStats(String userId) async {
    try {
      final records = await getUserRecords(userId);
      final tagStats = <String, int>{};
      
      for (var record in records) {
        for (var tag in record.tags) {
          tagStats[tag] = (tagStats[tag] ?? 0) + 1;
        }
      }
      
      return tagStats;
    } catch (e) {
      _logger.e('Error getting tag stats: $e');
      rethrow;
    }
  }

  @override
  Future<Map<String, int>> getCategoryStats(String userId) async {
    try {
      final records = await getUserRecords(userId);
      final categoryStats = <String, int>{};
      
      for (var record in records) {
        categoryStats[record.category] = (categoryStats[record.category] ?? 0) + 1;
      }
      
      return categoryStats;
    } catch (e) {
      _logger.e('Error getting category stats: $e');
      rethrow;
    }
  }

  @override
  Future<Map<String, int>> getTimeStats(String userId, String groupBy) async {
    try {
      final records = await getUserRecords(userId);
      final timeStats = <String, int>{};
      
      for (var record in records) {
        final date = DateTime.parse(record.timestamp);
        String key;
        
        switch (groupBy.toLowerCase()) {
          case 'year':
            key = date.year.toString();
            break;
          case 'month':
            key = '${date.year}-${date.month.toString().padLeft(2, '0')}';
            break;
          case 'day':
            key = '${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}';
            break;
          default:
            throw ArgumentError('Unsupported groupBy: $groupBy');
        }
        
        timeStats[key] = (timeStats[key] ?? 0) + 1;
      }
      
      return timeStats;
    } catch (e) {
      _logger.e('Error getting time stats: $e');
      rethrow;
    }
  }
} 