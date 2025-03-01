import 'package:logger/logger.dart';
import '../../domain/entities/chat.dart';
import '../../domain/entities/message.dart';
import '../../domain/repositories/chat_repository.dart';
import '../datasources/chat_data_source.dart';
import '../models/chat_model.dart';
import '../models/message_model.dart';

/// 聊天仓库实现
/// 实现领域层定义的聊天仓库接口，连接数据源和领域层
class ChatRepositoryImpl implements ChatRepository {
  final ChatDataSource remoteDataSource;
  final ChatDataSource localDataSource;
  final Logger logger;

  ChatRepositoryImpl({
    required this.remoteDataSource,
    required this.localDataSource,
    required this.logger,
  });

  @override
  Future<List<Chat>> getUserChats(String userId, {int limit = 20, int offset = 0}) async {
    try {
      // 首先尝试从本地获取
      try {
        final localChats = await localDataSource.getUserChats(
          userId,
          limit: limit,
          offset: offset,
        );
        return localChats.map((model) => model.toEntity()).toList();
      } catch (_) {
        // 本地获取失败，从远程获取
        final remoteChats = await remoteDataSource.getUserChats(
          userId,
          limit: limit,
          offset: offset,
        );
        
        // 保存到本地
        for (final chat in remoteChats) {
          await localDataSource.createChat(chat);
        }
        
        return remoteChats.map((model) => model.toEntity()).toList();
      }
    } catch (e) {
      logger.e('获取用户聊天列表失败: $e');
      throw Exception('获取用户聊天列表失败');
    }
  }

  @override
  Future<List<Chat>> getChatsByType(String userId, ChatType type, {int limit = 20, int offset = 0}) async {
    try {
      final chatModels = await remoteDataSource.getChatsByType(
        userId,
        type.toString(),
        limit: limit,
        offset: offset,
      );
      
      // 保存到本地
      for (final chat in chatModels) {
        await localDataSource.createChat(chat);
      }
      
      return chatModels.map((model) => model.toEntity()).toList();
    } catch (e) {
      logger.e('获取特定类型的聊天列表失败: $e');
      throw Exception('获取特定类型的聊天列表失败');
    }
  }

  @override
  Future<Chat> getChatById(String chatId) async {
    try {
      // 首先尝试从本地获取
      try {
        final localChat = await localDataSource.getChatById(chatId);
        return localChat.toEntity();
      } catch (_) {
        // 本地不存在，从远程获取
        final remoteChat = await remoteDataSource.getChatById(chatId);
        // 保存到本地
        await localDataSource.createChat(remoteChat);
        return remoteChat.toEntity();
      }
    } catch (e) {
      logger.e('获取聊天详情失败: $e');
      throw Exception('获取聊天详情失败');
    }
  }

  @override
  Future<Chat> createChat(Chat chat) async {
    try {
      final chatModel = ChatModel.fromEntity(chat);
      final createdChat = await remoteDataSource.createChat(chatModel);
      await localDataSource.createChat(createdChat);
      return createdChat.toEntity();
    } catch (e) {
      logger.e('创建聊天失败: $e');
      throw Exception('创建聊天失败');
    }
  }

  @override
  Future<void> updateChat(Chat chat) async {
    try {
      final chatModel = ChatModel.fromEntity(chat);
      await remoteDataSource.updateChat(chatModel);
      await localDataSource.updateChat(chatModel);
    } catch (e) {
      logger.e('更新聊天信息失败: $e');
      throw Exception('更新聊天信息失败');
    }
  }

  @override
  Future<void> deleteChat(String chatId) async {
    try {
      await remoteDataSource.deleteChat(chatId);
      await localDataSource.deleteChat(chatId);
    } catch (e) {
      logger.e('删除聊天失败: $e');
      throw Exception('删除聊天失败');
    }
  }

  @override
  Future<List<Message>> getChatMessages(String chatId, {int limit = 50, int offset = 0}) async {
    try {
      // 首先尝试从本地获取
      try {
        final localMessages = await localDataSource.getChatMessages(
          chatId,
          limit: limit,
          offset: offset,
        );
        return localMessages.map((model) => model.toEntity()).toList();
      } catch (_) {
        // 本地获取失败，从远程获取
        final remoteMessages = await remoteDataSource.getChatMessages(
          chatId,
          limit: limit,
          offset: offset,
        );
        
        // 保存到本地
        for (final message in remoteMessages) {
          await localDataSource.sendMessage(message);
        }
        
        return remoteMessages.map((model) => model.toEntity()).toList();
      }
    } catch (e) {
      logger.e('获取聊天消息失败: $e');
      throw Exception('获取聊天消息失败');
    }
  }

  @override
  Future<Message> sendMessage(Message message) async {
    try {
      final messageModel = MessageModel.fromEntity(message);
      
      // 首先保存到本地以实现发送中状态
      await localDataSource.sendMessage(messageModel);
      
      // 发送到远程
      final sentMessage = await remoteDataSource.sendMessage(messageModel);
      
      // 更新本地状态
      await localDataSource.updateMessageStatus(
        sentMessage.id,
        sentMessage.status.toString(),
      );
      
      return sentMessage.toEntity();
    } catch (e) {
      logger.e('发送消息失败: $e');
      
      // 更新本地消息状态为发送失败
      try {
        await localDataSource.updateMessageStatus(
          message.id,
          MessageStatus.failed.toString(),
        );
      } catch (_) {}
      
      throw Exception('发送消息失败');
    }
  }

  @override
  Future<void> updateMessageStatus(String messageId, MessageStatus status) async {
    try {
      await remoteDataSource.updateMessageStatus(messageId, status.toString());
      await localDataSource.updateMessageStatus(messageId, status.toString());
    } catch (e) {
      logger.e('更新消息状态失败: $e');
      throw Exception('更新消息状态失败');
    }
  }

  @override
  Future<void> deleteMessage(String messageId) async {
    try {
      await remoteDataSource.deleteMessage(messageId);
      await localDataSource.deleteMessage(messageId);
    } catch (e) {
      logger.e('删除消息失败: $e');
      throw Exception('删除消息失败');
    }
  }

  @override
  Future<void> markMessagesAsRead(String chatId, String userId) async {
    try {
      await remoteDataSource.markMessagesAsRead(chatId, userId);
      await localDataSource.markMessagesAsRead(chatId, userId);
    } catch (e) {
      logger.e('标记消息为已读失败: $e');
      throw Exception('标记消息为已读失败');
    }
  }

  @override
  Future<int> getUnreadMessagesCount(String userId) async {
    try {
      return await remoteDataSource.getUnreadMessagesCount(userId);
    } catch (e) {
      logger.e('获取未读消息数量失败: $e');
      throw Exception('获取未读消息数量失败');
    }
  }

  @override
  Future<List<Message>> searchMessages(String userId, String query, {int limit = 20, int offset = 0}) async {
    try {
      final messageModels = await remoteDataSource.searchMessages(
        userId,
        query,
        limit: limit,
        offset: offset,
      );
      return messageModels.map((model) => model.toEntity()).toList();
    } catch (e) {
      logger.e('搜索聊天记录失败: $e');
      throw Exception('搜索聊天记录失败');
    }
  }

  @override
  Future<void> addUserToChat(String chatId, String userId) async {
    try {
      await remoteDataSource.addUserToChat(chatId, userId);
      
      // 更新本地聊天数据
      final chat = await localDataSource.getChatById(chatId);
      if (!chat.participantIds.contains(userId)) {
        final updatedParticipants = List<String>.from(chat.participantIds)..add(userId);
        await localDataSource.updateChat(
          chat.copyWith(participantIds: updatedParticipants),
        );
      }
    } catch (e) {
      logger.e('添加用户到聊天失败: $e');
      throw Exception('添加用户到聊天失败');
    }
  }

  @override
  Future<void> removeUserFromChat(String chatId, String userId) async {
    try {
      await remoteDataSource.removeUserFromChat(chatId, userId);
      
      // 更新本地聊天数据
      final chat = await localDataSource.getChatById(chatId);
      if (chat.participantIds.contains(userId)) {
        final updatedParticipants = List<String>.from(chat.participantIds)..remove(userId);
        await localDataSource.updateChat(
          chat.copyWith(participantIds: updatedParticipants),
        );
      }
    } catch (e) {
      logger.e('从聊天中移除用户失败: $e');
      throw Exception('从聊天中移除用户失败');
    }
  }

  @override
  Future<void> pinChat(String chatId, String userId) async {
    try {
      await remoteDataSource.pinChat(chatId, userId);
      
      // 更新本地聊天数据
      final chat = await localDataSource.getChatById(chatId);
      await localDataSource.updateChat(chat.copyWith(isPinned: true));
    } catch (e) {
      logger.e('置顶聊天失败: $e');
      throw Exception('置顶聊天失败');
    }
  }

  @override
  Future<void> unpinChat(String chatId, String userId) async {
    try {
      await remoteDataSource.unpinChat(chatId, userId);
      
      // 更新本地聊天数据
      final chat = await localDataSource.getChatById(chatId);
      await localDataSource.updateChat(chat.copyWith(isPinned: false));
    } catch (e) {
      logger.e('取消置顶聊天失败: $e');
      throw Exception('取消置顶聊天失败');
    }
  }

  @override
  Future<void> muteChat(String chatId, String userId) async {
    try {
      await remoteDataSource.muteChat(chatId, userId);
      
      // 更新本地聊天数据
      final chat = await localDataSource.getChatById(chatId);
      await localDataSource.updateChat(chat.copyWith(isMuted: true));
    } catch (e) {
      logger.e('静音聊天失败: $e');
      throw Exception('静音聊天失败');
    }
  }

  @override
  Future<void> unmuteChat(String chatId, String userId) async {
    try {
      await remoteDataSource.unmuteChat(chatId, userId);
      
      // 更新本地聊天数据
      final chat = await localDataSource.getChatById(chatId);
      await localDataSource.updateChat(chat.copyWith(isMuted: false));
    } catch (e) {
      logger.e('取消静音聊天失败: $e');
      throw Exception('取消静音聊天失败');
    }
  }

  @override
  Future<void> archiveChat(String chatId, String userId) async {
    try {
      await remoteDataSource.archiveChat(chatId, userId);
      
      // 更新本地聊天数据
      final chat = await localDataSource.getChatById(chatId);
      await localDataSource.updateChat(chat.copyWith(isArchived: true));
    } catch (e) {
      logger.e('归档聊天失败: $e');
      throw Exception('归档聊天失败');
    }
  }

  @override
  Future<void> unarchiveChat(String chatId, String userId) async {
    try {
      await remoteDataSource.unarchiveChat(chatId, userId);
      
      // 更新本地聊天数据
      final chat = await localDataSource.getChatById(chatId);
      await localDataSource.updateChat(chat.copyWith(isArchived: false));
    } catch (e) {
      logger.e('取消归档聊天失败: $e');
      throw Exception('取消归档聊天失败');
    }
  }

  @override
  Future<Message> sendAiMessage(String chatId, String userId, String content) async {
    try {
      // 创建用户消息
      final userMessage = Message.text(
        content: content,
        senderId: userId,
        chatId: chatId,
      );
      
      // 发送用户消息
      await sendMessage(userMessage);
      
      // 获取AI回复
      final aiReply = await getAiReply(chatId, content);
      
      return aiReply;
    } catch (e) {
      logger.e('发送AI消息失败: $e');
      throw Exception('发送AI消息失败');
    }
  }

  @override
  Future<Message> getAiReply(String chatId, String messageContent) async {
    try {
      // TODO: 这里应该调用AI服务获取回复
      // 暂时返回一个模拟的AI回复
      final aiMessage = Message(
        id: 'ai_${DateTime.now().millisecondsSinceEpoch}',
        content: '这是AI的自动回复: "$messageContent"',
        timestamp: DateTime.now(),
        senderId: 'ai_assistant',
        chatId: chatId,
        type: MessageType.text,
        status: MessageStatus.sent,
      );
      
      // 保存AI回复到数据源
      final messageModel = MessageModel.fromEntity(aiMessage);
      final savedMessage = await localDataSource.sendMessage(messageModel);
      
      return savedMessage.toEntity();
    } catch (e) {
      logger.e('获取AI回复失败: $e');
      throw Exception('获取AI回复失败');
    }
  }
}