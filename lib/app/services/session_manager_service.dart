import 'package:get/get.dart';
import '../data/models/chat.dart';

class SessionManagerService extends GetxService {
  // 会话列表
  final sessions = <Chat>[].obs;
  
  // 当前选中的会话
  final Rx<Chat?> currentSession = Rx<Chat?>(null);

  // 初始化
  Future<void> init() async {
    // TODO: 从本地存储或服务器加载会话列表
  }

  // 添加新会话
  void addSession(Chat chat) {
    sessions.add(chat);
    // TODO: 保存到本地存储
  }

  // 删除会话
  void removeSession(String chatId) {
    sessions.removeWhere((chat) => chat.id == chatId);
    // TODO: 从本地存储删除
  }

  // 更新会话
  void updateSession(Chat chat) {
    final index = sessions.indexWhere((s) => s.id == chat.id);
    if (index != -1) {
      sessions[index] = chat;
      // TODO: 更新本地存储
    }
  }

  // 选择会话
  void selectSession(Chat chat) {
    currentSession.value = chat;
  }

  // 清空会话
  void clearSessions() {
    sessions.clear();
    currentSession.value = null;
    // TODO: 清空本地存储
  }
} 