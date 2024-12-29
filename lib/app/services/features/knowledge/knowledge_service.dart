@singleton
class KnowledgeService {
  final NetworkService _network;
  final CacheService _cache;

  KnowledgeService(this._network, this._cache);

  Future<Map<String, dynamic>> getKnowledgeGraph(String topic) async {
    final cacheKey = 'graph_$topic';
    return await _cache.get(cacheKey) ?? await _fetchGraph(topic);
  }

  Future<Map<String, dynamic>> _fetchGraph(String topic) async {
    final response = await _network.get('/knowledge/graph/$topic');
    await _cache.set('graph_$topic', response.data, ttl: Duration(days: 1));
    return response.data;
  }
} 