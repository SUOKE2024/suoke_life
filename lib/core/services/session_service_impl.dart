import 'package:suoke_life/lib/core/services/infrastructure/redis_service.dart';
import 'package:suoke_life/lib/core/services/session_service.dart';
import 'package:uuid/uuid.dart';

class SessionServiceImpl implements SessionService {
  final RedisService _redisService;
  final String _sessionKeyPrefix = 'session:';
  final int _sessionTtl = 3600; // Session TTL in seconds

  SessionServiceImpl(this._redisService);

  @override
  Future<String> createSession(String userId) async {
    final sessionId = const Uuid().v4();
    final sessionKey = _sessionKeyPrefix + sessionId;
    await _redisService.hset(sessionKey, 'userId', userId);
    await _redisService.setex(sessionKey, _sessionTtl, 'active');
    return sessionId;
  }

  @override
  Future<String?> getUserId(String sessionId) async {
    final sessionKey = _sessionKeyPrefix + sessionId;
    return await _redisService.hget(sessionKey, 'userId');
  }

  @override
  Future<bool> isValidSession(String sessionId) async {
    final sessionKey = _sessionKeyPrefix + sessionId;
    final sessionStatus = await _redisService.get(sessionKey);
    return sessionStatus == 'active';
  }

  @override
  Future<void> invalidateSession(String sessionId) async {
    final sessionKey = _sessionKeyPrefix + sessionId;
    await _redisService.delete(sessionKey);
  }
} 
} 