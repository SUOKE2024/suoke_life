import 'package:get/get.dart';
import '../core/storage/storage_service.dart';
import '../data/models/life_record.dart';

class LifeService extends GetxService {
  final StorageService _storageService = Get.find();
  
  final records = <String, List<Map<String, dynamic>>>{}.obs;
  final categories = <String>[].obs;
  final tags = <String>[].obs;

  Future<LifeService> init() async {
    try {
      await Future.wait([
        _loadRecords(),
        _loadCategories(),
        _loadTags(),
      ]);
      return this;
    } catch (e) {
      print('Error initializing life service: $e');
      return this;
    }
  }

  Future<void> _loadRecords() async {
    try {
      final data = await _storageService.getLocal('life_records');
      if (data != null) {
        records.value = Map<String, List<Map<String, dynamic>>>.from(data);
      }
    } catch (e) {
      print('Error loading records: $e');
    }
  }

  Future<void> _loadCategories() async {
    try {
      final data = await _storageService.getLocal('life_categories');
      if (data != null) {
        categories.value = List<String>.from(data);
      }
    } catch (e) {
      print('Error loading categories: $e');
    }
  }

  Future<void> _loadTags() async {
    try {
      final data = await _storageService.getLocal('life_tags');
      if (data != null) {
        tags.value = List<String>.from(data);
      }
    } catch (e) {
      print('Error loading tags: $e');
    }
  }

  // 获取生活记录列表
  Future<List<LifeRecord>> getLifeRecords() async {
    try {
      final data = await _storageService.getAllDB('life_records');
      return data.map((map) => LifeRecord.fromMap(map)).toList();
    } catch (e) {
      print('Error getting life records: $e');
      return [];
    }
  }

  // 获取生活记录详情
  Future<LifeRecord?> getLifeRecord(String id) async {
    try {
      final data = await _storageService.getDB('life_records', id);
      if (data != null) {
        return LifeRecord.fromMap(data);
      }
      return null;
    } catch (e) {
      print('Error getting life record: $e');
      return null;
    }
  }

  // 保存生活记录
  Future<void> saveLifeRecord(LifeRecord record) async {
    try {
      await _storageService.saveDB('life_records', record.toMap());
    } catch (e) {
      print('Error saving life record: $e');
      rethrow;
    }
  }

  // 删除生活记录
  Future<void> deleteLifeRecord(String id) async {
    try {
      await _storageService.removeDB('life_records', id);
    } catch (e) {
      print('Error deleting life record: $e');
      rethrow;
    }
  }

  // 更新生活记录
  Future<void> updateLifeRecord(LifeRecord record) async {
    try {
      await _storageService.saveDB('life_records', record.toMap());
    } catch (e) {
      print('Error updating life record: $e');
      rethrow;
    }
  }

  // 搜索生活记录
  Future<List<LifeRecord>> searchLifeRecords(String keyword) async {
    try {
      final records = await getLifeRecords();
      return records.where((record) {
        return record.title.contains(keyword) || 
               record.content.contains(keyword) ||
               record.tags.any((tag) => tag.contains(keyword));
      }).toList();
    } catch (e) {
      print('Error searching life records: $e');
      return [];
    }
  }
} 