import '../models/user.dart';
import '../../domain/models/chat_message.dart';

abstract class UserRepository {
  Future<User> addUser(User user);
  Future<User?> getUserById(int id);
  Future<List<User>> getAllUsers();
  Future<User> updateUser(User user);
  Future<void> deleteUser(int id);
  Future<User?> getUserByEmail(String email);

  Future<void> setString(String key, String value);
  Future<String?> getStringValue(String key);

  Future<List<ChatMessage>> getChatHistory();
  Future<void> saveChatHistory(List<ChatMessage> chatHistory);
} 