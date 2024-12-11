import 'package:get/get.dart';
import 'leaderboard_model.dart';

class LeaderboardController extends GetxController {
  final isLoading = true.obs;
  final leaderboardItems = <LeaderboardItem>[].obs;

  @override
  void onInit() {
    super.onInit();
    loadLeaderboardData();
  }

  Future<void> loadLeaderboardData() async {
    try {
      isLoading.value = true;
      // TODO: 从API获取排行榜数据
      await Future.delayed(const Duration(seconds: 1)); // 模拟网络请求
      leaderboardItems.value = [
        LeaderboardItem('探索达人', 1000),
        LeaderboardItem('寻宝能手', 850),
        LeaderboardItem('冒险家', 720),
        LeaderboardItem('新手探险者', 500),
        LeaderboardItem('初级寻宝者', 300),
      ];
    } finally {
      isLoading.value = false;
    }
  }

  Future<void> refreshLeaderboard() async {
    await loadLeaderboardData();
  }
} 