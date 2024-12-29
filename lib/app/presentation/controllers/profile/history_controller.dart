import 'package:get/get.dart';
import '../../../services/features/suoke/suoke_service.dart';
import '../../../data/models/history_item.dart';

class HistoryController extends GetxController {
  final SuokeService suokeService;
  
  final isLoadingChat = false.obs;
  final isLoadingService = false.obs;
  final isLoadingExplore = false.obs;
  
  final chatHistory = <HistoryItem>[].obs;
  final serviceHistory = <HistoryItem>[].obs;
  final exploreHistory = <HistoryItem>[].obs;

  HistoryController(this.suokeService);

  @override
  void onInit() {
    super.onInit();
    loadAllHistory();
  }

  Future<void> loadAllHistory() async {
    await Future.wait([
      loadChatHistory(),
      loadServiceHistory(),
      loadExploreHistory(),
    ]);
  }

  Future<void> loadChatHistory() async {
    try {
      isLoadingChat.value = true;
      final result = await suokeService.getChatHistory();
      chatHistory.value = result;
    } catch (e) {
      Get.snackbar('错误', '加载聊天历史失败');
    } finally {
      isLoadingChat.value = false;
    }
  }

  Future<void> loadServiceHistory() async {
    try {
      isLoadingService.value = true;
      final result = await suokeService.getServiceHistory();
      serviceHistory.value = result;
    } catch (e) {
      Get.snackbar('错误', '加载服务历史失败');
    } finally {
      isLoadingService.value = false;
    }
  }

  Future<void> loadExploreHistory() async {
    try {
      isLoadingExplore.value = true;
      final result = await suokeService.getExploreHistory();
      exploreHistory.value = result;
    } catch (e) {
      Get.snackbar('错误', '加载探索历史失败');
    } finally {
      isLoadingExplore.value = false;
    }
  }

  void openChat(HistoryItem chat) {
    Get.toNamed('/chat/detail', arguments: chat.id);
  }

  void openService(HistoryItem service) {
    Get.toNamed('/suoke/service/${service.id}', arguments: service);
  }

  void openExplore(HistoryItem explore) {
    Get.toNamed('/explore/topic/${explore.id}', arguments: explore);
  }
} 