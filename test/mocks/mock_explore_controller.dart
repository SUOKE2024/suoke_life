import 'package:get/get.dart';
import 'package:suoke_app/app/presentation/controllers/explore/explore_controller.dart';
import 'package:suoke_app/app/services/features/suoke/suoke_service.dart';
import 'package:suoke_app/app/data/models/explore_item.dart';

class MockExploreController extends ExploreController {
  @override
  final SuokeService suokeService;

  MockExploreController({required this.suokeService}) : super(suokeService) {
    // 初始化测试数据
    exploreItems.value = [
      ExploreItem(
        id: '1',
        title: 'Test Topic',
        content: 'Test Content',
        type: 'article',
      ),
    ];
  }

  @override
  void onInit() {
    // 不调用 super.onInit() 以避免实际的网络请求
  }

  @override
  Future<void> loadExploreItems() async {
    // 不执行实际的加载操作
  }
} 