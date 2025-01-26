abstract class RedisService {
  Future<void> init();
  Future<void> set(String key, String value, {Duration? expiry});
  Future<String?> get(String key);
  Future<void> delete(String key);
  Future<bool> exists(String key);
  Future<void> publish(String channel, String message);
  Stream<String> subscribe(String channel);
}
