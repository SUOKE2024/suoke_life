import 'package:get/get.dart';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';
import 'ai_service.dart';

class RecommendationService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();
  final AiService _aiService = Get.find();

  // 健康建议推荐
  Future<List<Map<String, dynamic>>> recommendHealthAdvice(Map<String, dynamic> userProfile) async {
    try {
      // 分析用户健康数据
      final healthData = await _analyzeHealthData(userProfile);
      
      // 生成个性化建议
      final recommendations = await _generateRecommendations(healthData);
      
      // 排序和过滤
      return _rankAndFilterRecommendations(recommendations);
    } catch (e) {
      await _loggingService.log('error', 'Failed to recommend health advice', data: {'error': e.toString()});
      return [];
    }
  }

  // 生活方式推荐
  Future<Map<String, List<String>>> recommendLifestyle(Map<String, dynamic> userProfile) async {
    try {
      // 分析用户生活习惯
      final lifestyleData = await _analyzeLifestyleData(userProfile);
      
      // 生成改进建议
      return {
        'diet': await _generateDietRecommendations(lifestyleData),
        'exercise': await _generateExerciseRecommendations(lifestyleData),
        'rest': await _generateRestRecommendations(lifestyleData),
        'activities': await _generateActivityRecommendations(lifestyleData),
      };
    } catch (e) {
      await _loggingService.log('error', 'Failed to recommend lifestyle', data: {'error': e.toString()});
      return {};
    }
  }

  // 内容推荐
  Future<List<Map<String, dynamic>>> recommendContent(String userId) async {
    try {
      // 获取用户兴趣
      final userInterests = await _getUserInterests(userId);
      
      // 获取候选内容
      final candidates = await _getContentCandidates(userInterests);
      
      // 计算相似度
      final scoredContent = await _scoreContent(candidates, userInterests);
      
      // 排序和过滤
      return _rankAndFilterContent(scoredContent);
    } catch (e) {
      await _loggingService.log('error', 'Failed to recommend content', data: {'error': e.toString()});
      return [];
    }
  }

  Future<Map<String, dynamic>> _analyzeHealthData(Map<String, dynamic> userProfile) async {
    try {
      return await _aiService.queryKnowledge(
        'analyze_health_data',
        parameters: userProfile,
      );
    } catch (e) {
      rethrow;
    }
  }

  Future<List<Map<String, dynamic>>> _generateRecommendations(Map<String, dynamic> healthData) async {
    try {
      final response = await _aiService.queryKnowledge(
        'generate_health_recommendations',
        parameters: healthData,
      );
      return List<Map<String, dynamic>>.from(response['recommendations'] ?? []);
    } catch (e) {
      rethrow;
    }
  }

  List<Map<String, dynamic>> _rankAndFilterRecommendations(List<Map<String, dynamic>> recommendations) {
    try {
      // 按优先级排序
      recommendations.sort((a, b) => (b['priority'] ?? 0).compareTo(a['priority'] ?? 0));
      
      // 过滤掉不适合的建议
      return recommendations.where((r) => _isRecommendationValid(r)).toList();
    } catch (e) {
      rethrow;
    }
  }

  Future<Map<String, dynamic>> _analyzeLifestyleData(Map<String, dynamic> userProfile) async {
    try {
      return await _aiService.queryKnowledge(
        'analyze_lifestyle',
        parameters: userProfile,
      );
    } catch (e) {
      rethrow;
    }
  }

  Future<List<String>> _generateDietRecommendations(Map<String, dynamic> lifestyleData) async {
    try {
      final response = await _aiService.queryKnowledge(
        'recommend_diet',
        parameters: lifestyleData,
      );
      return List<String>.from(response['recommendations'] ?? []);
    } catch (e) {
      rethrow;
    }
  }

  Future<List<String>> _generateExerciseRecommendations(Map<String, dynamic> lifestyleData) async {
    try {
      final response = await _aiService.queryKnowledge(
        'recommend_exercise',
        parameters: lifestyleData,
      );
      return List<String>.from(response['recommendations'] ?? []);
    } catch (e) {
      rethrow;
    }
  }

  Future<List<String>> _generateRestRecommendations(Map<String, dynamic> lifestyleData) async {
    try {
      final response = await _aiService.queryKnowledge(
        'recommend_rest',
        parameters: lifestyleData,
      );
      return List<String>.from(response['recommendations'] ?? []);
    } catch (e) {
      rethrow;
    }
  }

  Future<List<String>> _generateActivityRecommendations(Map<String, dynamic> lifestyleData) async {
    try {
      final response = await _aiService.queryKnowledge(
        'recommend_activities',
        parameters: lifestyleData,
      );
      return List<String>.from(response['recommendations'] ?? []);
    } catch (e) {
      rethrow;
    }
  }

  Future<List<String>> _getUserInterests(String userId) async {
    try {
      final userData = await _storageService.getLocal('user_interests_$userId');
      return List<String>.from(userData ?? []);
    } catch (e) {
      rethrow;
    }
  }

  Future<List<Map<String, dynamic>>> _getContentCandidates(List<String> interests) async {
    try {
      final response = await _aiService.queryKnowledge(
        'get_content_candidates',
        parameters: {'interests': interests},
      );
      return List<Map<String, dynamic>>.from(response['candidates'] ?? []);
    } catch (e) {
      rethrow;
    }
  }

  Future<List<Map<String, dynamic>>> _scoreContent(
    List<Map<String, dynamic>> candidates,
    List<String> userInterests,
  ) async {
    print('Scoring content based on user interests...');
    // 示例：根据用户兴趣计算内容评分
    // 实际实现中需要根据具体业务逻辑计算评分
    return candidates.map((content) {
      final score = userInterests.fold<int>(0, (sum, interest) {
        return sum + (content['tags'].contains(interest) ? 1 : 0);
      });
      return {...content, 'score': score};
    }).toList();
  }

  List<Map<String, dynamic>> _rankAndFilterContent(List<Map<String, dynamic>> content) {
    try {
      // 按评分排序
      content.sort((a, b) => (b['score'] ?? 0).compareTo(a['score'] ?? 0));
      
      // 过滤低分内容
      return content.where((c) => (c['score'] ?? 0) > 0.5).toList();
    } catch (e) {
      rethrow;
    }
  }

  bool _isRecommendationValid(Map<String, dynamic> recommendation) {
    // TODO: 实现建议有效性检查
    return true;
  }

  bool _checkSuggestionValidity(Map<String, dynamic> suggestion) {
    print('Checking suggestion validity...');
    // 示例：检查建议的有效性
    // 实际实现中需要根据具体业务逻辑检查有效性
    return suggestion['score'] > 0;
  }
} 