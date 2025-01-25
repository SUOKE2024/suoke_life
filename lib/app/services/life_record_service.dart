import 'package:get/get.dart';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';

class LifeRecordService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();

  final records = <String, List<Map<String, dynamic>>>{}.obs;
  final categories = <String>[].obs;
  final tags = <String>[].obs;

  @override
  void onInit() {
    super.onInit();
    _initLifeRecord();
  }

  Future<void> _initLifeRecord() async {
    try {
      await Future.wait([
        _loadRecords(),
        _loadCategories(),
        _loadTags(),
      ]);
    } catch (e) {
      await _loggingService.log('error', 'Failed to initialize life record', data: {'error': e.toString()});
    }
  }

  // 添加记录
  Future<void> addRecord(
    String category,
    Map<String, dynamic> record, {
    List<String>? tags,
  }) async {
    try {
      final newRecord = {
        ...record,
        'category': category,
        'tags': tags ?? [],
        'created_at': DateTime.now().toIso8601String(),
      };

      if (!records.containsKey(category)) {
        records[category] = [];
      }
      records[category]!.insert(0, newRecord);

      await _saveRecords();
      await _updateTags(tags);
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
  }) async {
    try {
      if (!records.containsKey(category)) {
        throw Exception('Category not found: $category');
      }

      final index = records[category]!.indexWhere((r) => r['id'] == recordId);
      if (index == -1) {
        throw Exception('Record not found: $recordId');
      }

      records[category]![index] = {
        ...records[category]![index],
        ...updates,
        'tags': newTags ?? records[category]![index]['tags'],
        'updated_at': DateTime.now().toIso8601String(),
      };

      await _saveRecords();
      if (newTags != null) {
        await _updateTags(newTags);
      }
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

      records[category]!.removeWhere((r) => r['id'] == recordId);
      await _saveRecords();
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
        // 关键词过滤
        if (keyword != null && keyword.isNotEmpty) {
          final content = record['content'].toString().toLowerCase();
          if (!content.contains(keyword.toLowerCase())) {
            return false;
          }
        }

        // 标签过滤
        if (tags != null && tags.isNotEmpty) {
          final recordTags = List<String>.from(record['tags']);
          if (!tags.any((tag) => recordTags.contains(tag))) {
            return false;
          }
        }

        // 日期过滤
        final timestamp = DateTime.parse(record['created_at']);
        if (startDate != null && timestamp.isBefore(startDate)) {
          return false;
        }
        if (endDate != null && timestamp.isAfter(endDate)) {
          return false;
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
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    try {
      final stats = {
        'total_records': 0,
        'records_by_category': <String, int>{},
        'records_by_tag': <String, int>{},
        'daily_records': <String, int>{},
      };

      for (final category in records.keys) {
        final categoryRecords = records[category]!.where((record) {
          final timestamp = DateTime.parse(record['created_at']);
          if (startDate != null && timestamp.isBefore(startDate)) return false;
          if (endDate != null && timestamp.isAfter(endDate)) return false;
          return true;
        }).toList();

        // 更新总记录数
        stats['total_records'] = (stats['total_records'] as int) + categoryRecords.length;

        // 更新分类统计
        stats['records_by_category'][category] = categoryRecords.length;

        // 更新标签统计
        for (final record in categoryRecords) {
          final recordTags = List<String>.from(record['tags']);
          for (final tag in recordTags) {
            stats['records_by_tag'][tag] = (stats['records_by_tag'][tag] ?? 0) + 1;
          }

          // 更新每日统计
          final date = DateTime.parse(record['created_at']).toIso8601String().split('T')[0];
          stats['daily_records'][date] = (stats['daily_records'][date] ?? 0) + 1;
        }
      }

      return stats;
    } catch (e) {
      await _loggingService.log('error', 'Failed to get statistics', data: {'error': e.toString()});
      return {};
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

  Future<void> _saveRecords() async {
    try {
      await _storageService.saveLocal('life_records', records.value);
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
} 