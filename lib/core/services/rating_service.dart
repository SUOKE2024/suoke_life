import 'package:get/get.dart';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';

class RatingService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();

  final ratings = <Map<String, dynamic>>[].obs;
  final averageRating = 0.0.obs;
  final totalRatings = 0.obs;

  @override
  void onInit() {
    super.onInit();
    _initRating();
  }

  Future<void> _initRating() async {
    try {
      await _loadRatings();
      _calculateAverageRating();
    } catch (e) {
      await _loggingService.log('error', 'Failed to initialize rating', data: {'error': e.toString()});
    }
  }

  // 提交评分
  Future<void> submitRating({
    required double rating,
    required String userId,
    String? comment,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      final ratingData = {
        'rating': rating,
        'user_id': userId,
        'comment': comment,
        'metadata': metadata,
        'timestamp': DateTime.now().toIso8601String(),
      };

      ratings.insert(0, ratingData);
      await _saveRating(ratingData);
      _calculateAverageRating();
    } catch (e) {
      await _loggingService.log('error', 'Failed to submit rating', data: {'error': e.toString()});
      rethrow;
    }
  }

  // 更新评分
  Future<void> updateRating({
    required String userId,
    required double newRating,
    String? newComment,
    Map<String, dynamic>? newMetadata,
  }) async {
    try {
      final index = ratings.indexWhere((r) => r['user_id'] == userId);
      if (index == -1) {
        throw Exception('Rating not found');
      }

      final updatedRating = {
        ...ratings[index],
        'rating': newRating,
        'comment': newComment ?? ratings[index]['comment'],
        'metadata': newMetadata ?? ratings[index]['metadata'],
        'updated_at': DateTime.now().toIso8601String(),
      };

      ratings[index] = updatedRating;
      await _saveRatings();
      _calculateAverageRating();
    } catch (e) {
      await _loggingService.log('error', 'Failed to update rating', data: {'error': e.toString()});
      rethrow;
    }
  }

  // 删除评分
  Future<void> deleteRating(String userId) async {
    try {
      ratings.removeWhere((r) => r['user_id'] == userId);
      await _saveRatings();
      _calculateAverageRating();
    } catch (e) {
      await _loggingService.log('error', 'Failed to delete rating', data: {'error': e.toString()});
      rethrow;
    }
  }

  // 获取评分统计
  Future<Map<String, dynamic>> getRatingStats() async {
    try {
      return {
        'average_rating': averageRating.value,
        'total_ratings': totalRatings.value,
        'rating_distribution': _calculateRatingDistribution(),
        'recent_ratings': _getRecentRatings(10),
        'rating_trends': await _analyzeRatingTrends(),
      };
    } catch (e) {
      await _loggingService.log('error', 'Failed to get rating stats', data: {'error': e.toString()});
      return {};
    }
  }

  Future<void> _loadRatings() async {
    try {
      final savedRatings = await _storageService.getLocal('ratings');
      if (savedRatings != null) {
        ratings.value = List<Map<String, dynamic>>.from(savedRatings);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveRating(Map<String, dynamic> rating) async {
    try {
      ratings.insert(0, rating);
      await _saveRatings();
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveRatings() async {
    try {
      await _storageService.saveLocal('ratings', ratings);
    } catch (e) {
      rethrow;
    }
  }

  void _calculateAverageRating() {
    if (ratings.isEmpty) {
      averageRating.value = 0.0;
      totalRatings.value = 0;
      return;
    }

    final sum = ratings.fold<double>(
      0.0,
      (sum, rating) => sum + (rating['rating'] as double),
    );
    
    averageRating.value = sum / ratings.length;
    totalRatings.value = ratings.length;
  }

  Map<String, int> _calculateRatingDistribution() {
    final distribution = <String, int>{};
    for (final rating in ratings) {
      final score = rating['rating'].toString();
      distribution[score] = (distribution[score] ?? 0) + 1;
    }
    return distribution;
  }

  List<Map<String, dynamic>> _getRecentRatings(int count) {
    return ratings.take(count).toList();
  }

  Future<Map<String, dynamic>> _analyzeRatingTrends() async {
    try {
      final trends = <String, dynamic>{};
      
      // 按月分组
      final monthlyRatings = <String, List<double>>{};
      for (final rating in ratings) {
        final date = DateTime.parse(rating['timestamp']);
        final month = '${date.year}-${date.month.toString().padLeft(2, '0')}';
        monthlyRatings[month] = monthlyRatings[month] ?? [];
        monthlyRatings[month]!.add(rating['rating']);
      }

      // 计算每月平均分
      for (final entry in monthlyRatings.entries) {
        final sum = entry.value.reduce((a, b) => a + b);
        trends[entry.key] = sum / entry.value.length;
      }

      return trends;
    } catch (e) {
      rethrow;
    }
  }
} 