import 'package:get/get.dart';
import '../data/models/explore_item.dart';
import '../core/storage/storage_service.dart';

class ExploreService extends GetxService {
  final StorageService _storageService = Get.find();

  Future<List<ExploreItem>> getExploreItems() async {
    try {
      final data = await _storageService.getRemote('explore_items');
      return (data as List).map((e) => ExploreItem.fromJson(e)).toList();
    } catch (e) {
      return [];
    }
  }

  Future<ExploreItem?> getExploreItemDetail(String id) async {
    try {
      final data = await _storageService.getRemote('explore_item_$id');
      return ExploreItem.fromJson(data);
    } catch (e) {
      return null;
    }
  }
} 