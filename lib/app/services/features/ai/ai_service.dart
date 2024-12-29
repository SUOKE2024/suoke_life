import 'package:get/get.dart';
import '../base_feature_service.dart';
import '../../../core/network/network_service.dart';
import '../../../core/cache/cache_service.dart';

@singleton
class AIService {
  final NetworkService _network;
  final CacheService _cache;

  AIService(this._network, this._cache);

  // 小艾 - 生活助手
  Future<String> chatWithXiaoI(String message) async {
    final response = await _network.post('/ai/xiaoi/chat', {
      'message': message,
      'context': await _getContext(),
    });
    return response.data['reply'];
  }

  // 老克 - 知识助手
  Future<Map<String, dynamic>> askLaoKe(String question) async {
    final cacheKey = 'laoke_${question.hashCode}';
    final cached = await _cache.get<Map<String, dynamic>>(cacheKey);
    if (cached != null) return cached;

    final response = await _network.post('/ai/laoke/ask', {
      'question': question,
      'use_rag': true,
    });
    
    await _cache.set(cacheKey, response.data, ttl: Duration(hours: 24));
    return response.data;
  }

  // 小克 - 商务助手
  Future<Map<String, dynamic>> consultXiaoKe(String topic) async {
    return (await _network.post('/ai/xiaoke/consult', {
      'topic': topic,
      'business_context': await _getBusinessContext(),
    })).data;
  }
} 