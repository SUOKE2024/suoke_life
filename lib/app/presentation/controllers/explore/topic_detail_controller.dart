import 'package:get/get.dart';
import '../../../services/features/suoke/suoke_service.dart';
import '../../../data/models/topic.dart';

class TopicDetailController extends GetxController {
  final SuokeService suokeService;
  final Topic topic;
  final isLoading = false.obs;
  final graphData = <String, dynamic>{}.obs;

  TopicDetailController({
    required this.suokeService,
    required this.topic,
  });

  @override
  void onInit() {
    super.onInit();
    loadData();
  }

  Future<void> loadData() async {
    try {
      isLoading.value = true;
      final graph = await suokeService.getKnowledgeGraph(topic.id);
      graphData.value = graph;
    } catch (e) {
      Get.snackbar('错误', '加载数据失败');
    } finally {
      isLoading.value = false;
    }
  }

  void shareTopic() {
    // TODO: 实现分享功能
  }

  void askLaoKe() {
    Get.toNamed('/chat/laoke', arguments: {
      'topic': topic,
      'context': 'explore',
    });
  }
} 