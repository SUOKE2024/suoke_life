class GetHealthMetricsUseCase implements UseCase<HealthMetrics, String> {
  final HealthRepository repository;
  final CacheManager cacheManager;
  
  Future<Either<Failure, HealthMetrics>> call(String userId) async {
    // 先从缓存获取
    final cachedData = await cacheManager.get<HealthMetrics>('health_$userId');
    if (cachedData != null) {
      return Right(cachedData);
    }
    
    // 从服务器获取
    try {
      final metrics = await repository.getHealthMetrics(userId);
      await cacheManager.set('health_$userId', metrics);
      return Right(metrics);
    } catch (e) {
      return Left(ServerFailure());
    }
  }
} 