import 'package:redis/redis.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

abstract class RedisService {
  Future<void> connect();
  Future<void> disconnect();
  Future<String?> get(String key);
  Future<void> set(String key, String value, {Duration? expiry});
  Future<void> hset(String key, String field, String value);
  Future<String?> hget(String key, String field);
  Future<void> hdel(String key, String field);
  Future<void> delete(String key);
}

class RedisServiceImpl implements RedisService {
  RedisConnection? _connection;
  bool _isConnected = false;

  RedisServiceImpl() {
    connect();
  }

  @override
  Future<void> connect() async {
    if (_isConnected && _connection != null) {
      return;
    }
    final host = dotenv.env['REDIS_HOST'] ?? 'localhost';
    final port = int.parse(dotenv.env['REDIS_PORT'] ?? '6379');
    try {
      _connection = await RedisConnection.connect(host, port);
      _isConnected = true;
      print('Redis connected to $host:$port');
    } catch (e) {
      _isConnected = false;
      print('Failed to connect to Redis: $e');
      _connection = null;
    }
  }

  @override
  Future<void> disconnect() async {
    if (_isConnected && _connection != null) {
      try {
        await _connection!.close();
        _isConnected = false;
        _connection = null;
        print('Redis disconnected');
      } catch (e) {
        print('Error disconnecting from Redis: $e');
      }
    }
  }

  Future<RedisConnection> get connection async {
    if (!_isConnected || _connection == null) {
      await connect();
      if (!_isConnected || _connection == null) {
        throw Exception('Redis is not connected');
      }
    }
    return _connection!;
  }

  @override
  Future<String?> get(String key) async {
    final conn = await connection;
    final command = await conn.get(key);
    return command?.toString();
  }

  @override
  Future<void> set(String key, String value, {Duration? expiry}) async {
    final conn = await connection;
    await conn.set(key, value, expiry: expiry);
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
} 