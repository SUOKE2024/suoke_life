abstract class DataStorageService {
  Future<void> saveMessage(ChatMessage message);
  
  Future<List<ChatMessage>> getMessages({
    required String userId,
    required String assistantName,
    int limit = 20,
  });
  
  Future<void> clearMessages({
    required String userId,
    required String assistantName,
  });
  
  Future<void> initialize();
} 