import 'package:get/get.dart';
import 'package:suoke_life/data/models/game_history.dart';
import 'package:suoke_life/services/game_service.dart';

class GameHistoryController extends GetxController {
  final GameService _gameService = Get.find();
  final isLoading = true.obs;
  final history = <GameHistory>[].obs;

  @override
  void onInit() {
    super.onInit();
    loadHistory();
  }

  Future<void> loadHistory() async {
    try {
      isLoading.value = true;
      final records = await _gameService.getGameHistory();
      history.value = records;
    } catch (e) {
      Get.snackbar('错误', '加载游戏记录失败: $e');
    } finally {
      isLoading.value = false;
    }
  }

  Future<void> deleteHistory(String id) async {
    try {
      await _gameService.deleteGameHistory(id);
      history.removeWhere((record) => record.id == id);
      Get.snackbar('成功', '删除记录成功');
    } catch (e) {
      Get.snackbar('错误', '删除记录失败: $e');
    }
  }
} 