import '../../../core/network/network_service.dart';
import '../../../core/cache/cache_service.dart';

abstract class KnowledgeService {
  Future<Map<String, dynamic>> getKnowledgeGraph(String topic);
}

class KnowledgeServiceImpl implements KnowledgeService {
  final NetworkService _network;
  final CacheService _cache;

  KnowledgeServiceImpl(this._network, this._cache);

  @override
  Future<Map<String, dynamic>> getKnowledgeGraph(String topic) async {
    final cacheKey = 'graph_$topic';
    return await _cache.get(cacheKey) ?? await _fetchGraph(topic);
  }

  Future<Map<String, dynamic>> _fetchGraph(String topic) async {
    final response = await _network.get('/knowledge/graph/$topic');
    await _cache.set('graph_$topic', response.data,
        ttl: const Duration(days: 1));
    return response.data;
  }
}
