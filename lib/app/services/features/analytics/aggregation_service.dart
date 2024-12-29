@singleton
class AggregationService {
  final NetworkService _network;

  AggregationService(this._network);

  // 用户行为分析
  Future<Map<String, dynamic>> analyzeBehaviorPatterns() async {
    return (await _network.get('/analytics/aggregate/behavior')).data;
  }

  // 知识图谱分析
  Future<Map<String, dynamic>> analyzeKnowledgeGraph() async {
    return (await _network.get('/analytics/aggregate/knowledge')).data;
  }

  // 系统性能分析
  Future<Map<String, dynamic>> analyzeSystemPerformance() async {
    return (await _network.get('/analytics/aggregate/system')).data;
  }

  // 获取优化建议
  Future<List<Map<String, dynamic>>> getOptimizationSuggestions() async {
    return (await _network.get('/analytics/suggestions')).data;
  }
} 