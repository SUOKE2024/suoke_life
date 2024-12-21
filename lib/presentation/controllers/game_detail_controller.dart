import 'package:get/get.dart';
import 'package:suoke_life/data/models/game_detail.dart';
import 'package:suoke_life/services/game_service.dart';

class GameDetailController extends GetxController {
  final GameService _gameService = Get.find();
  final isLoading = true.obs;
  final gameDetail = Rx<GameDetail?>(null);

  @override
  void onInit() {
    super.onInit();
    final String gameId = Get.parameters['id'] ?? '';
    loadGameDetail(gameId);
  }

  Future<void> loadGameDetail(String gameId) async {
    try {
      isLoading.value = true;
      final detail = await _gameService.getGameDetail(gameId);
      gameDetail.value = detail;
    } catch (e) {
      Get.snackbar('错误', '加载游戏详情失败: $e');
    } finally {
      isLoading.value = false;
    }
  }

  void startGame() async {
    if (gameDetail.value == null) return;

    try {
      await _gameService.startGame(gameDetail.value!.id);
      Get.toNamed('/game/play/${gameDetail.value!.id}');
    } catch (e) {
      Get.snackbar('错误', '启动游戏失败: $e');
    }
  }
} 