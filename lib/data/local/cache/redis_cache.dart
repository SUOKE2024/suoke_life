import 'package:redis/redis.dart';

class RedisCache {
  late RedisConnection _conn;
  late Command _cmd;
  
  Future<void> init() async {
    _conn = RedisConnection();
    _cmd = await _conn.connect('localhost', 6379);
  }

  // 会话数据
  Future<void> setSessionData(String key, String value, {Duration? expiry}) async {
    await _cmd.send_object(["SET", key, value]);
    if (expiry != null) {
      await _cmd.send_object(["EXPIRE", key, expiry.inSeconds]);
    }
  }

  // 实时数据
  Future<void> setRealtimeData(String key, Map<String, dynamic> data) async {
    await _cmd.send_object(["HSET", key, ...data.entries.expand((e) => [e.key, e.value])]);
  }

  // 游戏临时数据
  Future<void> setGameData(String userId, Map<String, dynamic> data) async {
    final key = 'game:$userId';
    await _cmd.send_object(["HMSET", key, ...data.entries.expand((e) => [e.key, e.value])]);
    // 设置24小时过期
    await _cmd.send_object(["EXPIRE", key, 86400]);
  }
} 