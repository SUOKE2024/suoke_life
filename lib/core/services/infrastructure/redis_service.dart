import 'package:redis/redis.dart';

abstract class RedisService {
  Future<void> connect();
  Future<void> close();
  Future<String?> get(String key);
  Future<void> set(String key, String value, {int? seconds});
  Future<void> delete(String key);
  Future<void> hset(String key, String field, String value);
  Future<String?> hget(String key, String field);
  Future<void> hdel(String key, String field);
}

class RedisServiceImpl implements RedisService {
  late RedisConnection _connection;

  RedisServiceImpl() {
    _init();
  }

  Future<void> _init() async {
    final host = dotenv.env['REDIS_HOST'] ?? 'localhost';
    final port = int.parse(dotenv.env['REDIS_PORT'] ?? '6379');
    _connection = await RedisConnection.connect(host, port);
  }

  @override
  Future<String?> get(String key) async {
    final command = await _connection.get(key);
    return command;
  }

  @override
  Future<void> set(String key, String value, {int? seconds}) async {
    await _connection.set(key, value);
  }

  @override
  Future<void> close() async {
    await _connection.close();
  }

  @override
  Future<void> hset(String key, String field, String value) async {
    await _connection.hset(key, field, value);
  }

  @override
  Future<String?> hget(String key, String field) async {
    final response = await _connection.hget(key, field);
    if (response != null) {
      return response.toString();
    }
    return null;
  }

  @override
  Future<void> hdel(String key, String field) async {
    await _connection.hdel(key, field);
  }
} 