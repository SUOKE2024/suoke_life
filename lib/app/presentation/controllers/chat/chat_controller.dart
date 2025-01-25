import 'package:injectable/injectable.dart';
import 'package:flutter/foundation.dart';
import '../base/base_controller.dart';
import '../../../domain/services/chat_service.dart';
import '../../../domain/models/chat_message.dart';

@injectable
class ChatController extends BaseController {
  final ChatService _chatService;
  final messages = ValueNotifier<List<ChatMessage>>([]);

  ChatController(this._chatService);

  Future<void> loadMessages() async {
    try {
      setLoading(true);
      final result = await _chatService.getMessages();
      messages.value = result;
      setError(null);
    } catch (e) {
      setError(e.toString());
    } finally {
      setLoading(false);
    }
  }

  @override
  void dispose() {
    messages.dispose();
    super.dispose();
  }
} 