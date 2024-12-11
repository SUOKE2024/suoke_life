import 'package:get/get.dart';
import '../../core/routes/route_paths.dart';

class ExplorationModel {
  final String title;
  final String? subtitle;
  final String coverImage;
  final String route;
  final int onlineCount;
  final int popularity;
  final String visits;
  final double rating;

  ExplorationModel({
    required this.title,
    this.subtitle,
    required this.coverImage,
    required this.route,
    required this.onlineCount,
    required this.popularity,
    required this.visits,
    required this.rating,
  });
}

class ExploreController extends GetxController {
  final RxList<ExplorationModel> explorations = <ExplorationModel>[].obs;

  @override
  void onInit() {
    super.onInit();
    _loadExplorations();
  }

  void _loadExplorations() {
    // 模拟数据，实际应从API获取
    explorations.value = [
      ExplorationModel(
        title: '老克寻宝记',
        subtitle: '探索城市中的宝藏',
        coverImage: 'https://picsum.photos/400/300?random=1',
        route: RoutePaths.treasureQuest,
        onlineCount: 128,
        popularity: 95,
        visits: '1.2k',
        rating: 4.8,
      ),
      ExplorationModel(
        title: '城市探秘',
        subtitle: '发现身边的故事',
        coverImage: 'https://picsum.photos/400/300?random=2',
        route: RoutePaths.cityExplore,
        onlineCount: 86,
        popularity: 88,
        visits: '856',
        rating: 4.6,
      ),
      ExplorationModel(
        title: '文化寻踪',
        subtitle: '传统与现代的碰撞',
        coverImage: 'https://picsum.photos/400/300?random=3',
        route: RoutePaths.culturalQuest,
        onlineCount: 64,
        popularity: 92,
        visits: '723',
        rating: 4.7,
      ),
      ExplorationModel(
        title: '美食探店',
        subtitle: '发现城市味蕾',
        coverImage: 'https://picsum.photos/400/300?random=4',
        route: RoutePaths.foodExplore,
        onlineCount: 156,
        popularity: 96,
        visits: '1.5k',
        rating: 4.9,
      ),
    ];
  }
} 