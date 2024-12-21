import 'package:get/get.dart';
import 'package:suoke_life/data/models/game_ranking.dart';
import 'package:suoke_life/services/game_service.dart';

class GameRankingController extends GetxController {
  final GameService _gameService = Get.find();
  final isLoading = true.obs;
  final rankings = <GameRanking>[].obs;

  @override
  void onInit() {
    super.onInit();
    loadRankings();
  }

  Future<void> loadRankings() async {
    try {
      isLoading.value = true;
      final rankingList = await _gameService.getGameRankings();
      rankings.value = rankingList;
    } catch (e) {
      Get.snackbar('错误', '加载排行榜失败: $e');
    } finally {
      isLoading.value = false;
    }
  }

  Future<void> refreshRankings() async {
    await loadRankings();
  }
} 