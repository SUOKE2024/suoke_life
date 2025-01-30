import 'package:injectable/injectable.dart';

@lazySingleton
class LocalStorageService {
  final Database _db;
  final EncryptionService _encryption;
  
  LocalStorageService(this._db, this._encryption);

  // 存储加密数据
  Future<void> savePrivateData(String type, Map<String, dynamic> data) async {
    final encryptedData = await _encryption.encrypt(data);
    await _db.insert(
      'private_data',
      {
        'type': type,
        'data': encryptedData,
        'updated_at': DateTime.now().toIso8601String(),
      },
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  // 读取加密数据
  Future<Map<String, dynamic>?> getPrivateData(String type) async {
    final result = await _db.query(
      'private_data',
      where: 'type = ?',
      whereArgs: [type],
    );
    
    if (result.isEmpty) return null;
    
    final encryptedData = result.first['data'] as String;
    return await _encryption.decrypt(encryptedData);
  }

  // 会话管理
  Future<void> saveSession(Map<String, dynamic> sessionData) async {
    await savePrivateData('session', sessionData);
  }

  // 聊天历史
  Future<void> saveChatMessage(ChatMessage message) async {
    final messages = await getChatHistory(message.chatId) ?? [];
    messages.add(message);
    await savePrivateData('chat:${message.chatId}', {'messages': messages});
  }

  Future<List<ChatMessage>?> getChatHistory(String chatId) async {
    final data = await getPrivateData('chat:$chatId');
    if (data == null) return null;
    return (data['messages'] as List).map((m) => ChatMessage.fromMap(m)).toList();
  }

  // 用户行为数据
  Future<void> trackBehavior(String action, Map<String, dynamic> details) async {
    final behaviors = await getPrivateData('behaviors') ?? {'actions': []};
    behaviors['actions'].add({
      'action': action,
      'details': details,
      'timestamp': DateTime.now().toIso8601String(),
    });
    await savePrivateData('behaviors', behaviors);
  }
} 