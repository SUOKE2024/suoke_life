import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:get/get.dart';
import 'package:path_provider/path_provider.dart';
import 'package:synchronized/synchronized.dart';
import '../core/error/error_handler.dart';
import '../core/error/error_types.dart';
import '../data/models/health_advice.dart';
import '../data/providers/health_advice_provider.dart';
import '../services/storage_service.dart';

class HealthAdviceService extends GetxService {
  final HealthAdviceProvider _provider;
  final advices = <HealthAdvice>[].obs;
  final isLoading = false.obs;
  final _storage = Get.find<StorageService>();
  final _cacheKey = 'health_advices';
  final favorites = <String>[].obs;
  final _favoritesKey = 'health_advice_favorites';
  final _historyKey = 'health_advice_history';
  final viewHistory = <String>[].obs;
  final _lock = Lock();

  HealthAdviceService({
    required HealthAdviceProvider provider,
  }) : _provider = provider;

  @override
  Future<void> onInit() async {
    super.onInit();
    try {
      await Future.wait([
        loadFavorites(),
        loadHistory(),
      ]);
    } catch (e) {
      ErrorHandler.handleError(e);
    }
  }

  Future<void> loadAdvices() async {
    await _lock.synchronized(() async {
      try {
        isLoading.value = true;
        final cached = await _loadCachedAdvices();
        if (cached.isNotEmpty) {
          advices.assignAll(cached);
        }
        final result = await _provider.getAdvices();
        advices.assignAll(result);
        await _cacheAdvices(result);
      } catch (e) {
        if (advices.isEmpty) {
          throw AppException(
            type: ErrorType.health,
            message: '加载健康建议失败',
          );
        }
      } finally {
        isLoading.value = false;
      }
    });
  }

  Future<HealthAdvice?> getAdviceDetail(String id) async {
    try {
      return await _provider.getAdviceDetail(id);
    } catch (e) {
      ErrorHandler.handleError(e);
      return null;
    }
  }

  List<HealthAdvice> getAdvicesByLevel(AdviceLevel level) {
    return advices.where((advice) => advice.level == level).toList();
  }

  List<HealthAdvice> getAdvicesByType(AdviceType type) {
    return advices.where((advice) => advice.type == type).toList();
  }

  List<HealthAdvice> getActiveAdvices() {
    return advices.where((advice) => !advice.isExpired).toList();
  }

  List<HealthAdvice> getUrgentAdvices() {
    return advices.where((a) => a.level == AdviceLevel.urgent).toList();
  }

  List<HealthAdvice> getHighPriorityAdvices() {
    return advices.where((a) => a.level == AdviceLevel.high).toList();
  }

  Future<void> _cacheAdvices(List<HealthAdvice> advices) async {
    try {
      final data = advices
          .where((a) => !a.isExpired)
          .map((e) => e.toJson())
          .toList();
      await _storage.saveLocal(_cacheKey, data);
    } catch (e) {
      ErrorHandler.handleError(e);
    }
  }

  Future<List<HealthAdvice>> _loadCachedAdvices() async {
    final data = await _storage.getLocal(_cacheKey);
    if (data != null) {
      return (data as List)
          .map((json) => HealthAdvice.fromJson(json))
          .toList();
    }
    return [];
  }

  Future<void> toggleFavorite(String adviceId) async {
    await _lock.synchronized(() async {
      try {
        if (favorites.contains(adviceId)) {
          favorites.remove(adviceId);
        } else {
          favorites.add(adviceId);
        }
        await _storage.saveLocal(_favoritesKey, favorites);
      } catch (e) {
        ErrorHandler.handleError(e);
        throw Exception('收藏操作失败');
      }
    });
  }

  Future<void> loadFavorites() async {
    final data = await _storage.getLocal(_favoritesKey);
    if (data != null) {
      favorites.assignAll(List<String>.from(data));
    }
  }

  Future<void> addToHistory(String adviceId) async {
    if (!viewHistory.contains(adviceId)) {
      viewHistory.insert(0, adviceId);
      if (viewHistory.length > 50) { // 限制历史记录数量
        viewHistory.removeLast();
      }
      await _storage.saveLocal(_historyKey, viewHistory);
    }
  }

  Future<void> loadHistory() async {
    final data = await _storage.getLocal(_historyKey);
    if (data != null) {
      viewHistory.assignAll(List<String>.from(data));
    }
  }

  Map<String, dynamic> getStatistics() {
    return {
      'total': advices.length,
      'urgent': advices.where((a) => a.level == AdviceLevel.urgent).length,
      'high': advices.where((a) => a.level == AdviceLevel.high).length,
      'medium': advices.where((a) => a.level == AdviceLevel.medium).length,
      'low': advices.where((a) => a.level == AdviceLevel.low).length,
      'byType': {
        for (var type in AdviceType.values)
          type.name: advices.where((a) => a.type == type).length
      },
      'tags': _getTagStatistics(),
    };
  }

  Map<String, int> _getTagStatistics() {
    final tagStats = <String, int>{};
    for (var advice in advices) {
      for (var tag in advice.tags) {
        tagStats[tag] = (tagStats[tag] ?? 0) + 1;
      }
    }
    return tagStats;
  }

  Future<String> exportToJson() async {
    final data = {
      'advices': advices.map((a) => a.toJson()).toList(),
      'favorites': favorites,
      'history': viewHistory,
      'statistics': getStatistics(),
    };
    return jsonEncode(data);
  }

  Future<void> exportToFile() async {
    await _lock.synchronized(() async {
      try {
        final json = await exportToJson();
        final directory = await getApplicationDocumentsDirectory();
        final file = File('${directory.path}/health_advices.json');
        await file.writeAsString(json, flush: true);
      } catch (e) {
        throw Exception('导出失败: $e');
      }
    });
  }

  Future<void> importFromFile() async {
    try {
      final directory = await getApplicationDocumentsDirectory();
      final file = File('${directory.path}/health_advices.json');
      if (!await file.exists()) {
        throw Exception('文件不存在');
      }
      final json = await file.readAsString();
      final data = jsonDecode(json);
      
      advices.assignAll((data['advices'] as List)
          .map((json) => HealthAdvice.fromJson(json))
          .toList());
      favorites.assignAll(List<String>.from(data['favorites']));
      viewHistory.assignAll(List<String>.from(data['history']));
      
      await _cacheAdvices(advices);
      await _storage.saveLocal(_favoritesKey, favorites);
      await _storage.saveLocal(_historyKey, viewHistory);
      
    } catch (e) {
      throw Exception('导入失败: $e');
    }
  }
} 