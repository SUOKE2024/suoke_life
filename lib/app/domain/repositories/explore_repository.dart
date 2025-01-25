import '../models/explore_item.dart';

abstract class ExploreRepository {
  Future<List<ExploreItem>> getExploreItems();
  Future<List<ExploreItem>> searchExploreItems(String query);
} 