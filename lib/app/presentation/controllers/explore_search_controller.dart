import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../data/models/explore_item.dart';
import '../../data/services/explore_service.dart';
import '../../routes/app_routes.dart';

class ExploreSearchController extends GetxController {
  final ExploreService _exploreService = Get.find();
  
  final searchController = TextEditingController();
  final searchText = ''.obs;
  final isLoading = false.obs;
  final searchResults = <ExploreItem>[].obs;
  final searchHistory = <String>[].obs;
  final hotSearches = <String>[
    '养生知识',
    '健康饮食',
    '运动指南',
    '睡眠改善',
    '情绪管理',
    '中医理论',
  ].obs;
  
  @override
  void onInit() {
    super.onInit();
    _loadSearchHistory();
    searchController.addListener(() {
      searchText.value = searchController.text;
      if (searchController.text.isEmpty) {
        searchResults.clear();
      }
    });
  }
  
  @override
  void onClose() {
    searchController.dispose();
    super.onClose();
  }
  
  Future<void> _loadSearchHistory() async {
    try {
      final history = await _exploreService.getSearchHistory();
      searchHistory.assignAll(history);
    } catch (e) {
      print('Failed to load search history: $e');
    }
  }
  
  Future<void> onSearch(String keyword) async {
    if (keyword.isEmpty) return;
    
    searchController.text = keyword;
    isLoading.value = true;
    
    try {
      // 添加到搜索历史
      if (!searchHistory.contains(keyword)) {
        searchHistory.insert(0, keyword);
        if (searchHistory.length > 10) {
          searchHistory.removeLast();
        }
        await _exploreService.saveSearchHistory(searchHistory);
      }
      
      // 执行搜索
      final results = await _exploreService.search(keyword);
      searchResults.assignAll(results);
    } catch (e) {
      Get.snackbar(
        '搜索失败',
        '请检查网络连接后重试',
        snackPosition: SnackPosition.BOTTOM,
      );
    } finally {
      isLoading.value = false;
    }
  }
  
  void clearSearch() {
    searchController.clear();
    searchResults.clear();
  }
  
  Future<void> clearHistory() async {
    final confirmed = await Get.dialog<bool>(
      AlertDialog(
        title: const Text('确认清空'),
        content: const Text('确定要清空搜索历史吗？'),
        actions: [
          TextButton(
            onPressed: () => Get.back(result: false),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () => Get.back(result: true),
            child: const Text('确定'),
          ),
        ],
      ),
    );
    
    if (confirmed == true) {
      searchHistory.clear();
      await _exploreService.clearSearchHistory();
    }
  }
  
  Future<void> removeFromHistory(String keyword) async {
    searchHistory.remove(keyword);
    await _exploreService.saveSearchHistory(searchHistory);
  }
  
  void showItemDetail(ExploreItem item) {
    Get.toNamed(
      AppRoutes.EXPLORE_DETAIL,
      arguments: item,
    );
  }
} 