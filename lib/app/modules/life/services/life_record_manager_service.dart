import 'package:get/get.dart';
import '../../../core/storage/storage_service.dart';
import '../../../services/logging_service.dart';

class LifeRecordManagerService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();

  // 生活记录数据
  final records = <String, List<Map<String, dynamic>>>{}.obs;
  final categories = <String>[].obs;
  final tags = <String>[].obs;
  final statistics = <String, Map<String, dynamic>>{}.obs;

  @override
  void onInit() {
    super.onInit();
    _initLifeRecordManager();
  }

  Future<void> _initLifeRecordManager() async {
    try {
      await Future.wait([
        _loadRecords(),
        _loadCategories(),
        _loadTags(),
        _loadStatistics(),
      ]);
      _startStatisticsCollection();
    } catch (e) {
      await _loggingService.log('error', 'Failed to initialize life record manager', data: {'error': e.toString()});
    }
  }

  // 添加记录
  Future<void> addRecord(
    String category,
    Map<String, dynamic> record, {
    List<String>? tags,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      final newRecord = {
        ...record,
        'category': category,
        'tags': tags ?? [],
        'metadata': metadata ?? {},
        'created_at': DateTime.now().toIso8601String(),
      };

      if (!records.containsKey(category)) {
        records[category] = [];
      }
      records[category]!.insert(0, newRecord);

      await _saveRecords();
      await _updateTags(tags);
      await _updateStatistics(category, newRecord);
    } catch (e) {
      await _loggingService.log('error', 'Failed to add record', data: {'category': category, 'error': e.toString()});
      rethrow;
    }
  }

  // 更新记录
  Future<void> updateRecord(
    String category,
    String recordId,
    Map<String, dynamic> updates, {
    List<String>? newTags,
    Map<String, dynamic>? newMetadata,
  }) async {
    try {
      if (!records.containsKey(category)) {
        throw Exception('Category not found: $category');
      }

      final index = records[category]!.indexWhere((r) => r['id'] == recordId);
      if (index == -1) {
        throw Exception('Record not found: $recordId');
      }

      final oldRecord = records[category]![index];
      final updatedRecord = {
        ...oldRecord,
        ...updates,
        'tags': newTags ?? oldRecord['tags'],
        'metadata': newMetadata ?? oldRecord['metadata'],
        'updated_at': DateTime.now().toIso8601String(),
      };

      records[category]![index] = updatedRecord;
      await _saveRecords();
      
      if (newTags != null) {
        await _updateTags(newTags);
      }
      
      await _updateStatistics(category, updatedRecord, oldRecord: oldRecord);
    } catch (e) {
      await _loggingService.log('error', 'Failed to update record', data: {'record_id': recordId, 'error': e.toString()});
      rethrow;
    }
  }

  // 删除记录
  Future<void> deleteRecord(String category, String recordId) async {
    try {
      if (!records.containsKey(category)) {
        throw Exception('Category not found: $category');
      }

      final record = records[category]!.firstWhere((r) => r['id'] == recordId);
      records[category]!.removeWhere((r) => r['id'] == recordId);
      
      await _saveRecords();
      await _updateStatistics(category, null, oldRecord: record);
    } catch (e) {
      await _loggingService.log('error', 'Failed to delete record', data: {'record_id': recordId, 'error': e.toString()});
      rethrow;
    }
  }

  // 搜索记录
  Future<List<Map<String, dynamic>>> searchRecords({
    String? keyword,
    String? category,
    List<String>? tags,
    DateTime? startDate,
    DateTime? endDate,
    Map<String, dynamic>? filters,
  }) async {
    try {
      var results = <Map<String, dynamic>>[];

      // 收集所有记录
      if (category != null) {
        if (records.containsKey(category)) {
          results.addAll(records[category]!);
        }
      } else {
        for (final categoryRecords in records.values) {
          results.addAll(categoryRecords);
        }
      }

      // 应用过滤条件
      results = results.where((record) {
        // 关键词搜索
        if (keyword != null) {
          final content = record.toString().toLowerCase();
          if (!content.contains(keyword.toLowerCase())) {
            return false;
          }
        }

        // 标签过滤
        if (tags != null && tags.isNotEmpty) {
          final recordTags = List<String>.from(record['tags'] ?? []);
          if (!tags.any((tag) => recordTags.contains(tag))) {
            return false;
          }
        }

        // 日期过滤
        if (startDate != null || endDate != null) {
          final timestamp = DateTime.parse(record['created_at']);
          if (startDate != null && timestamp.isBefore(startDate)) return false;
          if (endDate != null && timestamp.isAfter(endDate)) return false;
        }

        // 自定义过滤器
        if (filters != null) {
          for (final entry in filters.entries) {
            if (!_matchesFilter(record, entry.key, entry.value)) {
              return false;
            }
          }
        }

        return true;
      }).toList();

      return results;
    } catch (e) {
      await _loggingService.log('error', 'Failed to search records', data: {'error': e.toString()});
      return [];
    }
  }

  // 获取统计信息
  Future<Map<String, dynamic>> getStatistics({
    String? category,
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    try {
      if (category != null) {
        return statistics[category] ?? {};
      }

      final allStats = <String, dynamic>{
        'total_records': 0,
        'records_by_category': <String, int>{},
        'records_by_tag': <String, int>{},
        'daily_records': <String, int>{},
      };

      for (final categoryStats in statistics.values) {
        // 合并统计数据
        allStats['total_records'] += categoryStats['total_records'] ?? 0;
        
        final recordsByCategory = categoryStats['records_by_category'] as Map<String, int>?;
        if (recordsByCategory != null) {
          for (final entry in recordsByCategory.entries) {
            allStats['records_by_category'][entry.key] = 
              (allStats['records_by_category'][entry.key] ?? 0) + entry.value;
          }
        }
        
        final recordsByTag = categoryStats['records_by_tag'] as Map<String, int>?;
        if (recordsByTag != null) {
          for (final entry in recordsByTag.entries) {
            allStats['records_by_tag'][entry.key] = 
              (allStats['records_by_tag'][entry.key] ?? 0) + entry.value;
          }
        }
        
        final dailyRecords = categoryStats['daily_records'] as Map<String, int>?;
        if (dailyRecords != null) {
          for (final entry in dailyRecords.entries) {
            allStats['daily_records'][entry.key] = 
              (allStats['daily_records'][entry.key] ?? 0) + entry.value;
          }
        }
      }

      return allStats;
    } catch (e) {
      await _loggingService.log('error', 'Failed to get statistics', data: {'error': e.toString()});
      return {};
    }
  }

  void _startStatisticsCollection() {
    // TODO: 实现统计数据收集
  }

  bool _matchesFilter(
    Map<String, dynamic> record,
    String key,
    dynamic value,
  ) {
    try {
      final recordValue = record[key];
      if (recordValue == null) return false;

      if (value is List) {
        return value.contains(recordValue);
      } else if (value is Map) {
        if (value.containsKey('min') && recordValue < value['min']) return false;
        if (value.containsKey('max') && recordValue > value['max']) return false;
        return true;
      } else {
        return recordValue == value;
      }
    } catch (e) {
      return false;
    }
  }

  Future<void> _updateStatistics(
    String category,
    Map<String, dynamic>? newRecord, {
    Map<String, dynamic>? oldRecord,
  }) async {
    try {
      if (!statistics.containsKey(category)) {
        statistics[category] = {};
      }

      // 更新记录计数
      if (newRecord != null && oldRecord == null) {
        statistics[category]!['total_records'] = 
          (statistics[category]!['total_records'] ?? 0) + 1;
      } else if (newRecord == null && oldRecord != null) {
        statistics[category]!['total_records'] = 
          (statistics[category]!['total_records'] ?? 1) - 1;
      }

      // 更新标签统计
      if (oldRecord != null) {
        final oldTags = List<String>.from(oldRecord['tags'] ?? []);
        for (final tag in oldTags) {
          statistics[category]!['records_by_tag'][tag] = 
            (statistics[category]!['records_by_tag'][tag] ?? 1) - 1;
        }
      }
      
      if (newRecord != null) {
        final newTags = List<String>.from(newRecord['tags'] ?? []);
        for (final tag in newTags) {
          statistics[category]!['records_by_tag'][tag] = 
            (statistics[category]!['records_by_tag'][tag] ?? 0) + 1;
        }
      }

      // 更新日期统计
      if (oldRecord != null) {
        final oldDate = DateTime.parse(oldRecord['created_at'])
          .toIso8601String()
          .split('T')[0];
        statistics[category]!['daily_records'][oldDate] = 
          (statistics[category]!['daily_records'][oldDate] ?? 1) - 1;
      }
      
      if (newRecord != null) {
        final newDate = DateTime.parse(newRecord['created_at'])
          .toIso8601String()
          .split('T')[0];
        statistics[category]!['daily_records'][newDate] = 
          (statistics[category]!['daily_records'][newDate] ?? 0) + 1;
      }

      await _saveStatistics();
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _loadRecords() async {
    try {
      final saved = await _storageService.getLocal('life_records');
      if (saved != null) {
        records.value = Map<String, List<Map<String, dynamic>>>.from(saved);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveRecords() async {
    try {
      await _storageService.saveLocal('life_records', records.value);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _loadCategories() async {
    try {
      final saved = await _storageService.getLocal('record_categories');
      if (saved != null) {
        categories.value = List<String>.from(saved);
      } else {
        // 默认分类
        categories.value = [
          'daily',
          'work',
          'study',
          'exercise',
          'diet',
          'mood',
          'other',
        ];
        await _storageService.saveLocal('record_categories', categories);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _loadTags() async {
    try {
      final saved = await _storageService.getLocal('record_tags');
      if (saved != null) {
        tags.value = List<String>.from(saved);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _updateTags(List<String>? newTags) async {
    try {
      if (newTags == null || newTags.isEmpty) return;

      final updatedTags = Set<String>.from(tags)..addAll(newTags);
      tags.value = updatedTags.toList();
      await _storageService.saveLocal('record_tags', tags);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _loadStatistics() async {
    try {
      final saved = await _storageService.getLocal('record_statistics');
      if (saved != null) {
        statistics.value = Map<String, Map<String, dynamic>>.from(saved);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveStatistics() async {
    try {
      await _storageService.saveLocal('record_statistics', statistics.value);
    } catch (e) {
      rethrow;
    }
  }
} 