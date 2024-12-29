import 'package:suoke_app/app/domain/repositories/health_repository.dart';
import 'package:suoke_app/app/core/cache/cache_manager.dart';

class GetHealthMetricsUseCase {
  final HealthRepository repository;
  final CacheManager cacheManager;

  GetHealthMetricsUseCase({
    required this.repository,
    required this.cacheManager,
  });

  Future<Map<String, dynamic>> call() async {
    // 先尝试从缓存获取
    final cached = await cacheManager.get('health_metrics');
    if (cached != null) {
      return cached;
    }

    // 缓存未命中，从仓库获取
    final metrics = await repository.getHealthMetrics();
    await cacheManager.set('health_metrics', metrics);
    return metrics;
  }
} 