import 'package:redis/redis.dart';
import 'dart:convert';
import '../core/config/app_config.dart';

enum MessagePriority {
  high,
  medium,
  low,
}

class MessageQueueService {
  final RedisConnection _conn;
  late Command _cmd;
  
  MessageQueueService() : _conn = RedisConnection();

  Future<void> init() async {
    _cmd = await _conn.connect('localhost', 6379);
  }

  // 发送消息到队列
  Future<void> enqueue(
    String queue,
    Map<String, dynamic> message,
    {MessagePriority priority = MessagePriority.medium}
  ) async {
    final score = _getPriorityScore(priority);
    await _cmd.send_object([
      'ZADD',
      queue,
      score.toString(),
      jsonEncode(message),
    ]);
  }

  // 从队列获取消息
  Future<List<Map<String, dynamic>>> dequeue(
    String queue,
    int batchSize,
  ) async {
    final messages = await _cmd.send_object([
      'ZRANGE',
      queue,
      '0',
      (batchSize - 1).toString(),
      'WITHSCORES',
    ]);

    if (messages == null) return [];

    final List<Map<String, dynamic>> result = [];
    for (var i = 0; i < messages.length; i += 2) {
      try {
        final message = jsonDecode(messages[i]);
        result.add(message);
        
        // 删除已处理的消息
        await _cmd.send_object(['ZREM', queue, messages[i]]);
      } catch (e) {
        print('解析消息失败: $e');
      }
    }

    return result;
  }

  // 延迟消息
  Future<void> scheduleMessage(
    String queue,
    Map<String, dynamic> message,
    Duration delay,
  ) async {
    final deliveryTime = DateTime.now().add(delay).millisecondsSinceEpoch;
    await _cmd.send_object([
      'ZADD',
      'delayed:$queue',
      deliveryTime.toString(),
      jsonEncode(message),
    ]);
  }

  // 处理延迟消息
  Future<void> processDelayedMessages(String queue) async {
    final now = DateTime.now().millisecondsSinceEpoch;
    
    // 获取到期的消息
    final messages = await _cmd.send_object([
      'ZRANGEBYSCORE',
      'delayed:$queue',
      '0',
      now.toString(),
      'WITHSCORES',
    ]);

    if (messages == null) return;

    // 移动到主队列
    for (var i = 0; i < messages.length; i += 2) {
      await enqueue(queue, jsonDecode(messages[i]));
      await _cmd.send_object(['ZREM', 'delayed:$queue', messages[i]]);
    }
  }

  int _getPriorityScore(MessagePriority priority) {
    switch (priority) {
      case MessagePriority.high:
        return 100;
      case MessagePriority.medium:
        return 50;
      case MessagePriority.low:
        return 10;
    }
  }
} 