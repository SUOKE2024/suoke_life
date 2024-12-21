import 'package:get/get.dart';
import '../../models/message.dart';
import '../storage/chat_storage_service.dart';

class ChatSyncService {
  final ChatStorageService _storage;
  final _syncController = GetConnect();

  ChatSyncService(this._storage);

  Future<void> syncMessages() async {
    try {
      // 1. 获取本地消息
      final localMessages = await _storage.getMessages();
      
      // 2. 获取服务器消息
      final response = await _syncController.get('https://api.suoke.life/v1/sync/messages');
      
      if (!response.hasError) {
        final serverMessages = (response.body as List)
          .map((json) => Message.fromJson(json))
          .toList();
        
        // 3. 合并消息
        final mergedMessages = _mergeMessages(localMessages, serverMessages);
        
        // 4. 更新本地存储
        for (final message in mergedMessages) {
          await _storage.saveMessage(message);
        }
        
        // 5. 上传新消息到服务器
        final newMessages = _getNewMessages(localMessages, serverMessages);
        if (newMessages.isNotEmpty) {
          await _syncController.post(
            'https://api.suoke.life/v1/sync/messages',
            newMessages.map((m) => m.toJson()).toList(),
          );
        }
      }
    } catch (e) {
      print('Error in syncMessages: $e');
      throw Exception('同步失败');
    }
  }

  List<Message> _mergeMessages(List<Message> local, List<Message> server) {
    final merged = <Message>[];
    final seen = <String>{};

    // 合并逻辑:优先使用服务器版本
    for (final message in [...server, ...local]) {
      if (!seen.contains(message.id)) {
        merged.add(message);
        seen.add(message.id);
      }
    }

    return merged..sort((a, b) => a.timestamp.compareTo(b.timestamp));
  }

  List<Message> _getNewMessages(List<Message> local, List<Message> server) {
    final serverIds = server.map((m) => m.id).toSet();
    return local.where((m) => !serverIds.contains(m.id)).toList();
  }
} 