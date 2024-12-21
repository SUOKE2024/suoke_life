import 'package:redis/redis.dart';
import 'dart:async';

class DistributedLockService {
  final RedisConnection _conn;
  late Command _cmd;
  
  DistributedLockService() : _conn = RedisConnection();

  Future<void> init() async {
    _cmd = await _conn.connect('localhost', 6379);
  }

  // 获取锁
  Future<bool> acquireLock(
    String lockKey,
    String lockValue,
    Duration expiry,
  ) async {
    // 使用 SET NX 实现分布式锁
    final result = await _cmd.send_object([
      'SET',
      'lock:$lockKey',
      lockValue,
      'NX',
      'PX',
      expiry.inMilliseconds.toString(),
    ]);

    return result == 'OK';
  }

  // 释放锁
  Future<bool> releaseLock(String lockKey, String lockValue) async {
    // 使用 Lua 脚本确保原子性操作
    const script = '''
      if redis.call("get", KEYS[1]) == ARGV[1] then
        return redis.call("del", KEYS[1])
      else
        return 0
      end
    ''';

    final result = await _cmd.send_object([
      'EVAL',
      script,
      1,
      'lock:$lockKey',
      lockValue,
    ]);

    return result == 1;
  }

  // 自动续期���
  Future<void> startAutoRenewal(
    String lockKey,
    String lockValue,
    Duration renewInterval,
  ) async {
    Timer.periodic(renewInterval, (timer) async {
      try {
        const script = '''
          if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("pexpire", KEYS[1], ARGV[2])
          else
            return 0
          end
        ''';

        final result = await _cmd.send_object([
          'EVAL',
          script,
          1,
          'lock:$lockKey',
          lockValue,
          renewInterval.inMilliseconds.toString(),
        ]);

        if (result != 1) {
          timer.cancel();
        }
      } catch (e) {
        print('锁续期失败: $e');
        timer.cancel();
      }
    });
  }

  // 等待获取锁
  Future<bool> waitForLock(
    String lockKey,
    String lockValue,
    Duration timeout,
    Duration retryInterval,
  ) async {
    final stopTime = DateTime.now().add(timeout);
    
    while (DateTime.now().isBefore(stopTime)) {
      final acquired = await acquireLock(
        lockKey,
        lockValue,
        timeout,
      );
      
      if (acquired) return true;
      
      await Future.delayed(retryInterval);
    }
    
    return false;
  }
} 