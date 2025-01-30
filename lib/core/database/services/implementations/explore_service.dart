import 'package:get/get.dart';
import 'package:shared_preferences.dart';
import '../models/explore_item.dart';

class ExploreService extends GetxService {
  static const String _searchHistoryKey = 'explore_search_history';
  final SharedPreferences _prefs = Get.find();
  
  Future<List<String>> getSearchHistory() async {
    return _prefs.getStringList(_searchHistoryKey) ?? [];
  }
  
  Future<void> saveSearchHistory(List<String> history) async {
    await _prefs.setStringList(_searchHistoryKey, history);
  }
  
  Future<void> clearSearchHistory() async {
    await _prefs.remove(_searchHistoryKey);
  }
  
  Future<List<ExploreItem>> search(String keyword) async {
    // TODO: 实现实际的搜索逻辑
    await Future.delayed(const Duration(seconds: 1));
    
    // 模拟搜索结果
    return [
      ExploreItem(
        id: '1',
        title: '搜索结果 1',
        description: '这是一个与"$keyword"相关的内容',
        imageUrl: 'assets/images/explore/default.jpg',
        type: 'article',
        publishDate: DateTime.now(),
      ),
      ExploreItem(
        id: '2',
        title: '搜索结果 2',
        description: '这也是一个与"$keyword"相关的内容',
        imageUrl: 'assets/images/explore/default.jpg',
        type: 'video',
        publishDate: DateTime.now(),
      ),
    ];
  }
} 