import 'package:get/get.dart';
import '../../core/services/base_service.dart';
import '../../../data/models/explore_item.dart';

class ExploreService extends GetxService implements BaseService {
  final exploreItems = <ExploreItem>[].obs;
  final knowledgeGraph = <Map<String, dynamic>>[].obs;
  
  @override
  Future<void> init() async {
    await loadExploreItems();
  }

  @override
  Future<void> dispose() async {
    exploreItems.clear();
    knowledgeGraph.clear();
  }

  Future<void> loadExploreItems() async {
    // TODO: 从存储或API加载探索项目
    exploreItems.value = [
      ExploreItem(
        id: '1',
        title: '人工智能',
        subtitle: '探索AI的未来',
        imageUrl: 'assets/images/ai.jpg',
        content: '了解AI技术的最新发展...',
      ),
      ExploreItem(
        id: '2',
        title: '健康生活',
        subtitle: '关注身心健康',
        imageUrl: 'assets/images/health.jpg',
        content: '探索健康生活方式...',
      ),
    ];
  }

  Future<Map<String, dynamic>> getKnowledgeGraph(String topic) async {
    // TODO: 实现知识图谱查询
    return {};
  }

  Future<List<String>> searchTopics(String keyword) async {
    // TODO: 实现主题搜索
    return [];
  }
} 