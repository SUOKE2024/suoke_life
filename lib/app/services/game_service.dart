import 'package:get/get.dart';
import '../core/storage/storage_service.dart';

class GameService extends GetxService {
  final StorageService _storageService = Get.find();
  
  final currentGame = Rx<Map<String, dynamic>?>(null);
  final gameProgress = 0.0.obs;
  final gameScore = 0.obs;

  // 开始游戏
  Future<void> startGame(String gameType) async {
    try {
      final game = await _initializeGame(gameType);
      currentGame.value = game;
      gameProgress.value = 0.0;
      gameScore.value = 0;
      
      await _saveGameState();
    } catch (e) {
      rethrow;
    }
  }

  // 更新游戏进度
  Future<void> updateProgress(double progress, int score) async {
    try {
      gameProgress.value = progress;
      gameScore.value = score;
      
      await _saveGameState();
      
      if (progress >= 1.0) {
        await _completeGame();
      }
    } catch (e) {
      rethrow;
    }
  }

  // 获取排行榜
  Future<List<Map<String, dynamic>>> getLeaderboard(String gameType) async {
    try {
      final data = await _storageService.getLocal('game_leaderboard_$gameType');
      return data != null ? List<Map<String, dynamic>>.from(data) : [];
    } catch (e) {
      return [];
    }
  }

  Future<Map<String, dynamic>> _initializeGame(String gameType) async {
    // TODO: 初始化游戏配置
    return {};
  }

  Future<void> _saveGameState() async {
    if (currentGame.value == null) return;
    
    try {
      await _storageService.saveLocal('current_game', {
        ...currentGame.value!,
        'progress': gameProgress.value,
        'score': gameScore.value,
        'updated_at': DateTime.now().toIso8601String(),
      });
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _completeGame() async {
    if (currentGame.value == null) return;
    
    try {
      // 保存游戏记录
      final history = await _getGameHistory();
      history.add({
        'game_type': currentGame.value!['type'],
        'score': gameScore.value,
        'completed_at': DateTime.now().toIso8601String(),
      });
      await _storageService.saveLocal('game_history', history);
      
      // 更新排行榜
      await _updateLeaderboard();
      
      // 清除当前游戏
      currentGame.value = null;
    } catch (e) {
      rethrow;
    }
  }

  Future<List<Map<String, dynamic>>> _getGameHistory() async {
    try {
      final data = await _storageService.getLocal('game_history');
      return data != null ? List<Map<String, dynamic>>.from(data) : [];
    } catch (e) {
      return [];
    }
  }

  Future<void> _updateLeaderboard() async {
    if (currentGame.value == null) return;
    
    try {
      final leaderboard = await getLeaderboard(currentGame.value!['type']);
      leaderboard.add({
        'score': gameScore.value,
        'timestamp': DateTime.now().toIso8601String(),
      });
      
      // 排序并只保留前100名
      leaderboard.sort((a, b) => b['score'].compareTo(a['score']));
      if (leaderboard.length > 100) {
        leaderboard.removeRange(100, leaderboard.length);
      }
      
      await _storageService.saveLocal(
        'game_leaderboard_${currentGame.value!['type']}',
        leaderboard,
      );
    } catch (e) {
      rethrow;
    }
  }
} 