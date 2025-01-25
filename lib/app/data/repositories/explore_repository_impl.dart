import '../../domain/models/explore_item.dart';
import '../../domain/repositories/explore_repository.dart';

class ExploreRepositoryImpl implements ExploreRepository {
  @override
  Future<List<ExploreItem>> getExploreItems() async {
    // TODO: 实现真实的数据获取逻辑
    await Future.delayed(const Duration(seconds: 1));
    return [
      ExploreItem(
        id: '1',
        title: '探索项目 1',
        description: '这是探索项目 1 的描述',
        imageUrl: 'https://picsum.photos/200/300',
        createdAt: DateTime.now(),
      ),
      ExploreItem(
        id: '2',
        title: '探索项目 2',
        description: '这是探索项目 2 的描述',
        imageUrl: 'https://picsum.photos/200/300',
        createdAt: DateTime.now(),
      ),
      // 添加更多测试数据
    ];
  }

  @override
  Future<List<ExploreItem>> searchExploreItems(String query) async {
    final items = await getExploreItems();
    return items
        .where((item) =>
            item.title.toLowerCase().contains(query.toLowerCase()) ||
            item.description.toLowerCase().contains(query.toLowerCase()))
        .toList();
  }
} 