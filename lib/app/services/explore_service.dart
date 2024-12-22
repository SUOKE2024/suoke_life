import 'package:get/get.dart';
import '../core/storage/storage_service.dart';
import '../data/models/explore_item.dart';

class ExploreService extends GetxService {
  final StorageService _storageService = Get.find();

  // 获取探索内容列表
  Future<List<ExploreItem>> getExploreItems() async {
    try {
      final data = await _storageService.getAllDB('explore_items');
      return data.map((map) => ExploreItem.fromMap(map)).toList();
    } catch (e) {
      print('Error getting explore items: $e');
      return [];
    }
  }

  // 获取探索内容详情
  Future<ExploreItem?> getExploreItem(String id) async {
    try {
      final data = await _storageService.getDB('explore_items', id);
      if (data != null) {
        return ExploreItem.fromMap(data);
      }
      return null;
    } catch (e) {
      print('Error getting explore item: $e');
      return null;
    }
  }

  // 保存探索内容
  Future<void> saveExploreItem(ExploreItem item) async {
    try {
      await _storageService.saveDB('explore_items', item.toMap());
    } catch (e) {
      print('Error saving explore item: $e');
      rethrow;
    }
  }

  // 删除探索内容
  Future<void> deleteExploreItem(String id) async {
    try {
      await _storageService.removeDB('explore_items', id);
    } catch (e) {
      print('Error deleting explore item: $e');
      rethrow;
    }
  }
} 