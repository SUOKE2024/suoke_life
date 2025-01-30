import '../../../core/network/network_service.dart';
import '../../../data/models/topic.dart';

class ExploreService {
  final NetworkService _network;

  ExploreService(this._network);

  Future<Map<String, dynamic>> getKnowledgeGraph() async {
    final response = await _network.get('/explore/knowledge-graph');
    return response.data;
  }

  Future<List<Topic>> getTopics() async {
    final response = await _network.get('/explore/topics');
    return (response.data as List).map((json) => Topic.fromJson(json)).toList();
  }

  Future<List<Topic>> searchTopics(String keyword) async {
    final response = await _network.get(
      '/explore/topics/search',
      params: {'q': keyword},
    );
    return (response.data as List).map((json) => Topic.fromJson(json)).toList();
  }
} 