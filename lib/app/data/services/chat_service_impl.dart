import 'package:injectable/injectable.dart';
import '../../domain/services/chat_service.dart';
import '../../domain/models/chat_message.dart';
import '../providers/database_provider.dart';

@Injectable(as: ChatService) // 注册为 ChatService 接口
class ChatServiceImpl implements ChatService {
  final DatabaseProvider _db;

  ChatServiceImpl(this._db);

  @override
  Future<List<ChatMessage>> getMessages() async {
    final results = await _db.query('messages');
    return results.map((json) => ChatMessage.fromJson(json)).toList();
  }
} 