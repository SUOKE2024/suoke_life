import 'package:get/get.dart';
import 'package:suoke_life/services/search_history_service.dart';
import 'package:suoke_life/services/life_record_service.dart';
import 'package:suoke_life/data/models/life_record.dart';

class SearchController extends GetxController {
  final SearchHistoryService _searchHistoryService = Get.find();
  final LifeRecordService _recordService = Get.find();

  // 搜索历史
  final _searchHistory = <String>[].obs;
  List<String> get searchHistory => _searchHistory;

  // 热门搜索
  final _hotSearches = <String>[].obs;
  List<String> get hotSearches => _hotSearches;

  // 搜索建议
  final _searchSuggestions = <String>[].obs;
  List<String> get searchSuggestions => _searchSuggestions;

  // 搜索结果
  final _searchResults = <LifeRecord>[].obs;
  List<LifeRecord> get searchResults => _searchResults;

  // 当前搜索关键词
  final _currentQuery = ''.obs;
  String get currentQuery => _currentQuery.value;

  @override
  void onInit() {
    super.onInit();
    loadSearchHistory();
    loadHotSearches();
  }

  // 加载搜索历史
  void loadSearchHistory() {
    _searchHistory.value = _searchHistoryService.getSearchHistory();
  }

  // 加载热门搜索
  void loadHotSearches() {
    _hotSearches.value = _searchHistoryService.getHotSearches();
  }

  // 搜索内容变化
  void onSearchChanged(String query) {
    _currentQuery.value = query;
    if (query.isEmpty) {
      _searchSuggestions.clear();
      _searchResults.clear();
      return;
    }
    
    // 生成搜索建议
    _searchSuggestions.value = _generateSuggestions(query);
    
    // 执行搜索
    _performSearch(query);
  }

  // 生成搜索建议
  List<String> _generateSuggestions(String query) {
    final allRecords = _recordService.getAllRecords();
    final suggestions = <String>{};
    
    for (var record in allRecords) {
      if (record.content.toLowerCase().contains(query.toLowerCase())) {
        // 从内容中提取相关片段作为建议
        final words = record.content.split(' ');
        for (var word in words) {
          if (word.toLowerCase().contains(query.toLowerCase())) {
            suggestions.add(word);
          }
        }
      }
      
      // 从标签中提取建议
      for (var tag in record.tags) {
        if (tag.toLowerCase().contains(query.toLowerCase())) {
          suggestions.add(tag);
        }
      }
    }
    
    return suggestions.take(5).toList();
  }

  // 执行搜索
  void _performSearch(String query) {
    final allRecords = _recordService.getAllRecords();
    _searchResults.value = allRecords.where((record) {
      return record.content.toLowerCase().contains(query.toLowerCase()) ||
             record.tags.any((tag) => tag.toLowerCase().contains(query.toLowerCase()));
    }).toList();
  }

  // 点击历史记录
  void onHistoryTap(String query) {
    onSearchChanged(query);
    _searchHistoryService.addSearchHistory(query);
    loadSearchHistory();
  }

  // 点击搜索建议
  void onSuggestionTap(String suggestion) {
    onSearchChanged(suggestion);
    _searchHistoryService.addSearchHistory(suggestion);
    loadSearchHistory();
  }

  // 删除单条历史记录
  void removeSearchHistory(String query) async {
    await _searchHistoryService.removeSearchHistory(query);
    loadSearchHistory();
  }

  // 清空搜索历史
  void clearSearchHistory() async {
    await _searchHistoryService.clearSearchHistory();
    loadSearchHistory();
  }

  // 清空搜索
  void clearSearch() {
    _currentQuery.value = '';
    _searchSuggestions.clear();
    _searchResults.clear();
  }
} 