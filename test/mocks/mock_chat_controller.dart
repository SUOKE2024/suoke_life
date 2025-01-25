import 'package:get/get.dart';
import 'package:mockito/mockito.dart';
import '../../lib/app/presentation/controllers/chat/chat_controller.dart';
import '../../lib/app/data/models/chat_message.dart';

class MockChatController extends Mock implements ChatController {
  final _messages = <ChatMessage>[].obs;
  final _isLoading = false.obs;

  @override
  RxList<ChatMessage> get messages => _messages;

  @override
  RxBool get isLoading => _isLoading;

  @override
  Future<void> loadMessages() async {}

  @override
  void startChat(String assistantId) {}
} 