abstract class SessionService {
  Future<String?> getSessionId();
  Future<void> setSessionId(String sessionId);
  Future<void> clearSession();
} 