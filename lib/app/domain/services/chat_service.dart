import 'package:injectable/injectable.dart';
import '../models/chat_message.dart';
import 'base_service.dart';

abstract class ChatService extends BaseService {
  Future<List<ChatMessage>> getMessages();
} 