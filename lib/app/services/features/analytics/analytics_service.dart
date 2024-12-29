@singleton
class AnalyticsService {
  final LocalStorageService _storage;
  final NetworkService _network;
  final AnonymizerService _anonymizer;

  AnalyticsService(this._storage, this._network, this._anonymizer);

  // 收集用户行为数据
  Future<void> trackBehavior(String action, Map<String, dynamic> data) async {
    // 本地存储原始数据
    await _storage.trackBehavior(action, data);
    
    // 发送匿名化数据
    final anonymousData = _anonymizer.anonymizeBehaviorData({
      ...data,
      'actionType': action,
    });
    
    await _network.post('/analytics/behavior', anonymousData);
  }

  // 知识图谱增强
  Future<void> enhanceKnowledgeGraph(Map<String, dynamic> data) async {
    final anonymousData = _anonymizer.anonymizeKnowledgeData(data);
    await _network.post('/analytics/knowledge', anonymousData);
  }

  // 系统优化数据
  Future<void> reportSystemMetrics(Map<String, dynamic> metrics) async {
    final anonymousData = _anonymizer.anonymizeSystemData(metrics);
    await _network.post('/analytics/system', anonymousData);
  }

  // 获取聚合分析结果
  Future<Map<String, dynamic>> getAnalytics(String type) async {
    return (await _network.get('/analytics/$type')).data;
  }
} 