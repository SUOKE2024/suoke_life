import 'package:redis/redis.dart' as redis;
import 'package:flutter_dotenv/flutter_dotenv.dart';

abstract class RedisService {
  Future<void> connect(String host, int port);
  Future<String?> get(String key);
  Future<void> set(String key, String value, {Duration? expiry});
  Future<void> delete(String key);
  Future<void> hset(String key, String field, String value);
  Future<String?> hget(String key, String field);
  Future<void> hdel(String key, String field);
  Future<void> disconnect();
}

class RedisServiceImpl implements RedisService {
  redis.RedisConnection? _connection;
  bool _isConnected = false;

  RedisServiceImpl() {
    init();
  }

  @override
  Future<void> init() async {
    if (_isConnected && _connection != null) {
      return;
    }
    final host = dotenv.env['REDIS_HOST'] ?? 'localhost';
    final port = int.parse(dotenv.env['REDIS_PORT'] ?? '6379');
    try {
      _connection = await redis.RedisConnection.connect(host, port);
      _isConnected = true;
      print('Redis connected to $host:$port');
    } catch (e) {
      _isConnected = false;
      print('Failed to connect to Redis: $e');
      _connection = null;
    }
  }

  Future<redis.RedisConnection> get connection async {
    if (!_isConnected || _connection == null) {
      await init();
    }
    return _connection!;
  }

  @override
  Future<void> disconnect() async {
    if (_isConnected && _connection != null) {
      await _connection!.close();
      _isConnected = false;
      _connection = null;
      print('Redis disconnected');
    }
  }

  @override
  Future<String?> get(String key) async {
    final conn = await connection;
    final command = await conn.get(key);
    return command?.toString();
  }

  @override
  Future<void> set(String key, String value) async {
    final conn = await connection;
    await conn.set(key, value);
  }

  @override
  Future<void> hset(String key, String field, String value) async {
    final conn = await connection;
    await conn.hset(key, field, value);
  }

  @override
  Future<String?> hget(String key, String field) async {
    final conn = await connection;
    final response = await conn.hget(key, field);
    if (response != null) {
      return response.toString();
    }
    return null;
  }

  @override
  Future<void> hdel(String key, String field) async {
    final conn = await connection;
    await conn.hdel(key, field);
  }

  @override
  Future<void> delete(String key) async {
    final conn = await connection;
    await conn.delete(key);
  }

  @override
  Future<void> connect(String host, int port) async {
    final conn = await redis.RedisConnection.connect(host, port);
    // 其他逻辑
  }
} 