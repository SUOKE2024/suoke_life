import 'package:get/get.dart';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';

class TutorialService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();

  final tutorials = <String, Map<String, dynamic>>{}.obs;
  final completedTutorials = <String>[].obs;
  final currentTutorial = Rx<String?>(null);

  @override
  void onInit() {
    super.onInit();
    _initTutorials();
  }

  Future<void> _initTutorials() async {
    try {
      await _loadTutorials();
      await _loadCompletedTutorials();
    } catch (e) {
      await _loggingService.log('error', 'Failed to initialize tutorials', data: {'error': e.toString()});
    }
  }

  // 开始教程
  Future<void> startTutorial(String tutorialId) async {
    try {
      if (!tutorials.containsKey(tutorialId)) {
        throw Exception('Tutorial not found: $tutorialId');
      }

      currentTutorial.value = tutorialId;
      await _recordTutorialStart(tutorialId);
    } catch (e) {
      await _loggingService.log('error', 'Failed to start tutorial', data: {'tutorial_id': tutorialId, 'error': e.toString()});
      rethrow;
    }
  }

  // 完成教程
  Future<void> completeTutorial(String tutorialId) async {
    try {
      if (!tutorials.containsKey(tutorialId)) {
        throw Exception('Tutorial not found: $tutorialId');
      }

      completedTutorials.add(tutorialId);
      currentTutorial.value = null;
      await _saveCompletedTutorials();
      await _recordTutorialCompletion(tutorialId);
    } catch (e) {
      await _loggingService.log('error', 'Failed to complete tutorial', data: {'tutorial_id': tutorialId, 'error': e.toString()});
      rethrow;
    }
  }

  // 添加教程
  Future<void> addTutorial(String id, Map<String, dynamic> tutorial) async {
    try {
      tutorials[id] = tutorial;
      await _saveTutorials();
    } catch (e) {
      await _loggingService.log('error', 'Failed to add tutorial', data: {'tutorial_id': id, 'error': e.toString()});
      rethrow;
    }
  }

  // 重置教程进度
  Future<void> resetTutorials() async {
    try {
      completedTutorials.clear();
      currentTutorial.value = null;
      await _saveCompletedTutorials();
    } catch (e) {
      await _loggingService.log('error', 'Failed to reset tutorials', data: {'error': e.toString()});
      rethrow;
    }
  }

  // 检查教程是否完成
  bool isTutorialCompleted(String tutorialId) {
    return completedTutorials.contains(tutorialId);
  }

  // 获取下一个未完成的教程
  String? getNextTutorial() {
    try {
      return tutorials.keys.firstWhere(
        (id) => !completedTutorials.contains(id),
        orElse: () => '',
      );
    } catch (e) {
      return null;
    }
  }

  Future<void> _loadTutorials() async {
    try {
      final saved = await _storageService.getLocal('tutorials');
      if (saved != null) {
        tutorials.value = Map<String, Map<String, dynamic>>.from(saved);
      } else {
        await _loadDefaultTutorials();
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _loadDefaultTutorials() async {
    try {
      tutorials.value = {
        'basics': {
          'title': '基础功能教程',
          'description': '学习应用的基本功能和操作',
          'steps': [
            '欢迎使用',
            '主要功能介绍',
            '基本操作指南',
          ],
          'estimated_time': '5分钟',
        },
        'advanced': {
          'title': '高级功能教程',
          'description': '探索应用的高级功能',
          'steps': [
            '高级设置',
            '自定义配置',
            '性能优化',
          ],
          'estimated_time': '10分钟',
        },
      };
      await _saveTutorials();
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveTutorials() async {
    try {
      await _storageService.saveLocal('tutorials', tutorials);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _loadCompletedTutorials() async {
    try {
      final completed = await _storageService.getLocal('completed_tutorials');
      if (completed != null) {
        completedTutorials.value = List<String>.from(completed);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveCompletedTutorials() async {
    try {
      await _storageService.saveLocal('completed_tutorials', completedTutorials);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _recordTutorialStart(String tutorialId) async {
    try {
      final record = {
        'tutorial_id': tutorialId,
        'started_at': DateTime.now().toIso8601String(),
      };

      final history = await _getTutorialHistory();
      history.add(record);
      await _storageService.saveLocal('tutorial_history', history);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _recordTutorialCompletion(String tutorialId) async {
    try {
      final history = await _getTutorialHistory();
      final record = history.lastWhere(
        (r) => r['tutorial_id'] == tutorialId && r['completed_at'] == null,
        orElse: () => <String, dynamic>{},
      );

      if (record.isNotEmpty) {
        record['completed_at'] = DateTime.now().toIso8601String();
        await _storageService.saveLocal('tutorial_history', history);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<List<Map<String, dynamic>>> _getTutorialHistory() async {
    try {
      final history = await _storageService.getLocal('tutorial_history');
      return history != null ? List<Map<String, dynamic>>.from(history) : [];
    } catch (e) {
      return [];
    }
  }
} 