import 'package:suoke_life/core/services/infrastructure/redis_service.dart';
import 'package:injectable/injectable.dart';

@singleton
class CacheManager {
  final RedisService _redisService;

  CacheManager(this._redisService);

  Future<Map<String, dynamic>?> get(String key) async {
    final value = await _redisService.get(key);
    if (value != null) {
      return {'value': value};
    }
    return null;
  }

  Future<void> set(String key, Map<String, dynamic> value) async {
    await _redisService.set(key, value['value']);
  }

  Future<void> delete(String key) async {
    await _redisService.delete(key);
  }
} 