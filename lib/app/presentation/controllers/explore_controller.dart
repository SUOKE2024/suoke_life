import 'package:get/get.dart';
import '../../data/models/explore_item.dart';
import '../../services/explore_service.dart';

class ExploreController extends GetxController {
  final ExploreService _exploreService = Get.find();
  final exploreItems = <ExploreItem>[].obs;

  @override
  void onInit() {
    super.onInit();
    loadExploreItems();
  }

  Future<void> loadExploreItems() async {
    try {
      final items = await _exploreService.getExploreItems();
      exploreItems.value = items;
    } catch (e) {
      Get.snackbar('错误', '加载探索内容失败');
    }
  }

  void refreshItems() {
    loadExploreItems();
  }
} 