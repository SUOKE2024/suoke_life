import 'package:get/get.dart';
import '../../../services/features/suoke/suoke_service.dart';
import '../../../data/models/topic.dart';

class ExploreController extends GetxController {
  final SuokeService suokeService;
  final isLoading = false.obs;
  final topics = <Topic>[].obs;
  final graphData = <String, dynamic>{}.obs;

  ExploreController(this.suokeService);

  @override
  void onInit() {
    super.onInit();
    loadData();
  }

  Future<void> loadData() async {
    try {
      isLoading.value = true;
      // 加载知识图谱
      final graph = await suokeService.getKnowledgeGraph('all');
      graphData.value = graph;

      // 加载探索主题
      final result = await suokeService.getTopics();
      topics.value = result;
    } catch (e) {
      Get.snackbar('错误', '加载数据失败');
    } finally {
      isLoading.value = false;
    }
  }

  void showSearch() {
    // TODO: 实现搜索功能
  }

  void openTopic(Topic topic) {
    Get.toNamed('/explore/topic/${topic.id}', arguments: topic);
  }

  void showLaoKe() {
    Get.toNamed('/chat/laoke');
  }
} 