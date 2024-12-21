import 'package:get/get.dart';
import '../../data/models/chat.dart';
import '../../services/session_manager_service.dart';

class MessageController extends GetxController {
  final _sessionManager = Get.find<SessionManagerService>();
  
  final isLoading = false.obs;
  
  List<Chat> get sessions => _sessionManager.sessions;

  @override
  void onInit() {
    super.onInit();
    _loadSessions();
  }

  Future<void> _loadSessions() async {
    isLoading.value = true;
    try {
      await _sessionManager.init();
    } finally {
      isLoading.value = false;
    }
  }

  void openChat(Chat chat) {
    _sessionManager.selectSession(chat);
    Get.toNamed('/chat/${chat.id}');
  }
} 