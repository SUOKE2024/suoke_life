class RedisCacheService {
  final Redis _redis;
  
  // 会话管理
  Future<void> setSession(String userId, Map<String, dynamic> sessionData) async {
    await _redis.setex(
      'session:$userId',
      RedisCacheConfig.ttlConfig['user_session']!.inSeconds,
      json.encode(sessionData),
    );
  }
  
  // 热点数据缓存
  Future<List<Map<String, dynamic>>> getTrendingTopics() async {
    final cached = await _redis.get('trending:topics');
    if (cached != null) {
      return json.decode(cached);
    }
    // 从数据库获取并缓存
    final topics = await _fetchTrendingTopics();
    await _redis.setex(
      'trending:topics',
      RedisCacheConfig.ttlConfig['trending_topics']!.inSeconds,
      json.encode(topics),
    );
    return topics;
  }
  
  // AI对话上下文
  Future<void> setChatContext(String sessionId, List<Map<String, dynamic>> context) async {
    await _redis.setex(
      'chat:context:$sessionId',
      RedisCacheConfig.ttlConfig['chat_context']!.inSeconds,
      json.encode(context),
    );
  }
  
  // 分布式锁
  Future<bool> acquireLock(String resource, {Duration? timeout}) async {
    return await _redis.set(
      'lock:$resource',
      '1',
      nx: true,
      ex: timeout?.inSeconds ?? 10,
    ) != null;
  }
  
  // 计数器
  Future<void> incrementCounter(String key) async {
    await _redis.incr(key);
  }
  
  // 排行榜
  Future<void> updateLeaderboard(String userId, int score) async {
    await _redis.zadd('leaderboard', [score, userId]);
  }
  
  Future<List<String>> getTopUsers(int count) async {
    return await _redis.zrevrange('leaderboard', 0, count - 1);
  }
} 