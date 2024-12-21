import 'package:get/get.dart';
import 'package:hive/hive.dart';

class SearchHistoryService extends GetxService {
  static const String _boxName = 'search_history';
  late Box<String> _box;
  static const int maxHistoryItems = 20;

  // 初始化
  Future<void> init() async {
    _box = await Hive.openBox<String>(_boxName);
  }

  // 获取搜索历史
  List<String> getSearchHistory() {
    return _box.values.toList().reversed.toList();
  }

  // 添加搜索历史
  Future<void> addSearchHistory(String query) async {
    if (query.trim().isEmpty) return;

    // 如果已存在，先删除旧的
    final values = _box.values.toList();
    final index = values.indexOf(query);
    if (index != -1) {
      await _box.deleteAt(index);
    }

    // 添加到最后
    await _box.add(query);

    // 如果超过最大数量，删除最早的
    if (_box.length > maxHistoryItems) {
      await _box.deleteAt(0);
    }
  }

  // 删除单个搜索历史
  Future<void> removeSearchHistory(String query) async {
    final values = _box.values.toList();
    final index = values.indexOf(query);
    if (index != -1) {
      await _box.deleteAt(index);
    }
  }

  // 清空搜索历史
  Future<void> clearSearchHistory() async {
    await _box.clear();
  }

  // 获取热门搜索建议
  List<String> getHotSearches() {
    // TODO: 这里可以接入后端API获取真实的热门搜索
    return [
      '今天的心情',
      '美食记录',
      '旅行',
      '学习笔记',
      '生活感悟',
    ];
  }
} 