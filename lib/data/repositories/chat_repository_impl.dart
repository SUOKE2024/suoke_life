import 'package:suoke_life/domain/models/agent_model.dart';
import 'package:suoke_life/domain/models/chat_contact_model.dart';
import 'package:suoke_life/domain/models/doctor_model.dart';
import 'package:suoke_life/domain/models/provider_model.dart';
import 'package:suoke_life/domain/repositories/chat_repository.dart';

/// 聊天仓库实现
class ChatRepositoryImpl implements ChatRepository {
  // 模拟数据
  final List<ChatContact> _contacts = [];
  final Map<String, List<ChatMessage>> _messages = {};
  final Set<String> _favorites = {};
  
  // 单例模式
  static final ChatRepositoryImpl _instance = ChatRepositoryImpl._internal();
  
  // 工厂构造函数
  factory ChatRepositoryImpl() => _instance;
  
  // 内部构造函数
  ChatRepositoryImpl._internal() {
    _initializeMockData();
  }
  
  // 初始化模拟数据
  void _initializeMockData() {
    // 智能体联系人
    final agentContacts = [
      ChatContact(
        id: 'agent_xiaoai',
        name: '小艾',
        type: ChatContactType.agent,
        avatarUrl: 'assets/images/avatars/xiaoai.png',
        description: '您的智能生活助手',
        lastMessage: '有什么我能帮您的吗？',
        lastActiveTime: DateTime.now().subtract(const Duration(minutes: 5)),
        unreadCount: 1,
        extraData: {
          'agentType': AgentType.xiaoAi.toString(),
        },
      ),
      ChatContact(
        id: 'agent_xiaoke',
        name: '小克',
        type: ChatContactType.agent,
        avatarUrl: 'assets/images/avatars/xiaoke.png',
        description: '个人资源管理专家',
        lastMessage: '需要整理您的健康档案吗？',
        lastActiveTime: DateTime.now().subtract(const Duration(hours: 1)),
        unreadCount: 0,
        extraData: {
          'agentType': AgentType.xiaoKe.toString(),
        },
      ),
      ChatContact(
        id: 'agent_laoke',
        name: '老克',
        type: ChatContactType.agent,
        avatarUrl: 'assets/images/avatars/laoke.png',
        description: '中医文化知识专家',
        lastMessage: '点击了解更多中医药知识',
        lastActiveTime: DateTime.now().subtract(const Duration(hours: 3)),
        unreadCount: 0,
        extraData: {
          'agentType': AgentType.laoKe.toString(),
        },
      ),
      ChatContact(
        id: 'agent_suoer',
        name: '索儿',
        type: ChatContactType.agent,
        avatarUrl: 'assets/images/avatars/suoer.png',
        description: '您的健康管理专家',
        lastMessage: '您今天的健康报告已生成',
        lastActiveTime: DateTime.now().subtract(const Duration(hours: 6)),
        unreadCount: 2,
        extraData: {
          'agentType': AgentType.suoEr.toString(),
        },
      ),
    ];
    
    // 名医联系人
    final doctorContacts = [
      ChatContact(
        id: 'doctor_1',
        name: '张医生',
        type: ChatContactType.doctor,
        avatarUrl: 'assets/images/avatars/doctor_1.png',
        description: '主任医师 · 北京中医药大学附属医院',
        lastMessage: '请在挂号后与我联系',
        lastActiveTime: DateTime.now().subtract(const Duration(days: 1)),
        unreadCount: 0,
        extraData: {
          'title': DoctorTitle.chiefPhysician.toString(),
          'hospital': '北京中医药大学附属医院',
          'department': '针灸科',
          'rating': 4.9,
          'isOnline': false,
        },
      ),
      ChatContact(
        id: 'doctor_2',
        name: '李医生',
        type: ChatContactType.doctor,
        avatarUrl: 'assets/images/avatars/doctor_2.png',
        description: '副主任医师 · 上海中医药大学附属龙华医院',
        lastMessage: '您的舌象显示有湿热体质倾向',
        lastActiveTime: DateTime.now().subtract(const Duration(days: 2)),
        unreadCount: 0,
        extraData: {
          'title': DoctorTitle.associateChiefPhysician.toString(),
          'hospital': '上海中医药大学附属龙华医院',
          'department': '内科',
          'rating': 4.8,
          'isOnline': true,
        },
      ),
    ];
    
    // 供应商联系人
    final providerContacts = [
      ChatContact(
        id: 'provider_1',
        name: '同仁堂中医馆',
        type: ChatContactType.provider,
        avatarUrl: 'assets/images/avatars/provider_1.png',
        description: '中药药材与健康产品',
        lastMessage: '新品上架：温阳补气丸特惠中',
        lastActiveTime: DateTime.now().subtract(const Duration(days: 3)),
        unreadCount: 3,
        extraData: {
          'providerType': ProviderType.pharmacy.toString(),
        },
      ),
      ChatContact(
        id: 'provider_2',
        name: '御方堂中医馆',
        type: ChatContactType.provider,
        avatarUrl: 'assets/images/avatars/provider_2.png',
        description: '传统针灸推拿服务',
        lastMessage: '本周特惠：艾灸套餐7折',
        lastActiveTime: DateTime.now().subtract(const Duration(days: 4)),
        unreadCount: 0,
        extraData: {
          'providerType': ProviderType.clinic.toString(),
        },
      ),
    ];
    
    // 普通用户联系人
    final userContacts = [
      ChatContact(
        id: 'user_1',
        name: '王大志',
        type: ChatContactType.user,
        avatarUrl: 'assets/images/avatars/user_1.png',
        description: '养生达人',
        lastMessage: '我最近在尝试一种新的气功方法',
        lastActiveTime: DateTime.now().subtract(const Duration(days: 5)),
        unreadCount: 0,
      ),
      ChatContact(
        id: 'user_2',
        name: '李小燕',
        type: ChatContactType.user,
        avatarUrl: 'assets/images/avatars/user_2.png',
        description: '中医爱好者',
        lastMessage: '谢谢你推荐的艾灸方法，效果很好',
        lastActiveTime: DateTime.now().subtract(const Duration(days: 6)),
        unreadCount: 0,
      ),
    ];
    
    // 合并所有联系人
    _contacts.addAll([...agentContacts, ...doctorContacts, ...providerContacts, ...userContacts]);
    
    // 添加一些收藏联系人
    _favorites.add('agent_xiaoai');
    _favorites.add('doctor_1');
    _favorites.add('provider_1');
    
    // 为每个联系人初始化消息
    for (var contact in _contacts) {
      _messages[contact.id] = _generateMockMessages(contact.id);
    }
  }
  
  // 生成模拟消息数据
  List<ChatMessage> _generateMockMessages(String contactId) {
    final messages = <ChatMessage>[];
    final contact = _contacts.firstWhere((c) => c.id == contactId);
    
    // 根据联系人类型生成不同的对话内容
    if (contact.type == ChatContactType.agent) {
      messages.add(
        ChatMessage(
          id: '${contactId}_msg_1',
          senderId: contactId,
          receiverId: 'current_user',
          content: '您好，我是${contact.name}，有什么可以帮助您的吗？',
          type: ChatMessageType.text,
          sentTime: DateTime.now().subtract(const Duration(days: 1, hours: 2)),
          isRead: true,
        ),
      );
      
      messages.add(
        ChatMessage(
          id: '${contactId}_msg_2',
          senderId: 'current_user',
          receiverId: contactId,
          content: '我想了解一下我的体质类型',
          type: ChatMessageType.text,
          sentTime: DateTime.now().subtract(const Duration(days: 1, hours: 1)),
          isRead: true,
        ),
      );
      
      messages.add(
        ChatMessage(
          id: '${contactId}_msg_3',
          senderId: contactId,
          receiverId: 'current_user',
          content: '好的，我可以帮您进行体质评估。请告诉我您的一些基本症状和生活习惯，比如：您是否容易疲劳？睡眠质量如何？',
          type: ChatMessageType.text,
          sentTime: DateTime.now().subtract(const Duration(days: 1)),
          isRead: true,
        ),
      );
      
      if (contact.unreadCount > 0) {
        messages.add(
          ChatMessage(
            id: '${contactId}_msg_4',
            senderId: contactId,
            receiverId: 'current_user',
            content: contact.lastMessage ?? '有什么我能帮您的吗？',
            type: ChatMessageType.text,
            sentTime: DateTime.now().subtract(const Duration(minutes: 30)),
            isRead: false,
          ),
        );
      }
    } else if (contact.type == ChatContactType.doctor) {
      messages.add(
        ChatMessage(
          id: '${contactId}_msg_1',
          senderId: contactId,
          receiverId: 'current_user',
          content: '您好，我是${contact.name}，很高兴为您提供中医咨询服务。',
          type: ChatMessageType.text,
          sentTime: DateTime.now().subtract(const Duration(days: 3, hours: 5)),
          isRead: true,
        ),
      );
      
      messages.add(
        ChatMessage(
          id: '${contactId}_msg_2',
          senderId: 'current_user',
          receiverId: contactId,
          content: '医生您好，我最近睡眠不好，而且容易上火，请问是什么原因？',
          type: ChatMessageType.text,
          sentTime: DateTime.now().subtract(const Duration(days: 3, hours: 4)),
          isRead: true,
        ),
      );
      
      messages.add(
        ChatMessage(
          id: '${contactId}_msg_3',
          senderId: contactId,
          receiverId: 'current_user',
          content: '从您描述的症状来看，可能是阴虚火旺导致的问题。建议您可以适当调整饮食，增加一些滋阴清热的食物，如百合、莲子等。',
          type: ChatMessageType.text,
          sentTime: DateTime.now().subtract(const Duration(days: 3, hours: 3)),
          isRead: true,
        ),
      );
      
      if (contact.lastMessage != null) {
        messages.add(
          ChatMessage(
            id: '${contactId}_msg_4',
            senderId: contactId,
            receiverId: 'current_user',
            content: contact.lastMessage!,
            type: ChatMessageType.text,
            sentTime: DateTime.now().subtract(const Duration(days: 1, hours: 2)),
            isRead: true,
          ),
        );
      }
    } else if (contact.type == ChatContactType.provider) {
      messages.add(
        ChatMessage(
          id: '${contactId}_msg_1',
          senderId: contactId,
          receiverId: 'current_user',
          content: '欢迎光临${contact.name}，我们提供专业的中医健康服务和产品。',
          type: ChatMessageType.text,
          sentTime: DateTime.now().subtract(const Duration(days: 5, hours: 6)),
          isRead: true,
        ),
      );
      
      messages.add(
        ChatMessage(
          id: '${contactId}_msg_2',
          senderId: 'current_user',
          receiverId: contactId,
          content: '你们有养生茶吗？我想买一些缓解压力的。',
          type: ChatMessageType.text,
          sentTime: DateTime.now().subtract(const Duration(days: 5, hours: 5)),
          isRead: true,
        ),
      );
      
      messages.add(
        ChatMessage(
          id: '${contactId}_msg_3',
          senderId: contactId,
          receiverId: 'current_user',
          content: '有的，我们有多种养生茶，比如安神茶、菊花茶、玫瑰花茶等，都有不同的功效。您可以根据自己的需求选择。',
          type: ChatMessageType.text,
          sentTime: DateTime.now().subtract(const Duration(days: 5, hours: 4)),
          isRead: true,
        ),
      );
      
      if (contact.unreadCount > 0) {
        messages.add(
          ChatMessage(
            id: '${contactId}_msg_4',
            senderId: contactId,
            receiverId: 'current_user',
            content: contact.lastMessage ?? '感谢您对我们的支持，欢迎再次光临！',
            type: ChatMessageType.text,
            sentTime: DateTime.now().subtract(const Duration(days: 3)),
            isRead: false,
          ),
        );
      }
    } else if (contact.type == ChatContactType.user) {
      messages.add(
        ChatMessage(
          id: '${contactId}_msg_1',
          senderId: contactId,
          receiverId: 'current_user',
          content: '你好，我听说你最近在学习中医养生？',
          type: ChatMessageType.text,
          sentTime: DateTime.now().subtract(const Duration(days: 7, hours: 8)),
          isRead: true,
        ),
      );
      
      messages.add(
        ChatMessage(
          id: '${contactId}_msg_2',
          senderId: 'current_user',
          receiverId: contactId,
          content: '是的，我最近对中医很感兴趣，正在学习一些基础知识。',
          type: ChatMessageType.text,
          sentTime: DateTime.now().subtract(const Duration(days: 7, hours: 7)),
          isRead: true,
        ),
      );
      
      messages.add(
        ChatMessage(
          id: '${contactId}_msg_3',
          senderId: contactId,
          receiverId: 'current_user',
          content: '太好了，我有一些不错的资料可以分享给你。',
          type: ChatMessageType.text,
          sentTime: DateTime.now().subtract(const Duration(days: 7, hours: 6)),
          isRead: true,
        ),
      );
      
      if (contact.lastMessage != null) {
        messages.add(
          ChatMessage(
            id: '${contactId}_msg_4',
            senderId: contactId,
            receiverId: 'current_user',
            content: contact.lastMessage!,
            type: ChatMessageType.text,
            sentTime: DateTime.now().subtract(const Duration(days: 6)),
            isRead: true,
          ),
        );
      }
    }
    
    return messages;
  }

  @override
  Future<List<ChatContact>> getAllContacts() async {
    // 模拟网络延迟
    await Future.delayed(const Duration(milliseconds: 300));
    return _contacts;
  }

  @override
  Future<List<ChatContact>> getFavoriteContacts() async {
    // 模拟网络延迟
    await Future.delayed(const Duration(milliseconds: 200));
    return _contacts.where((contact) => _favorites.contains(contact.id)).toList();
  }

  @override
  Future<List<ChatContact>> getRecentContacts(int limit) async {
    // 模拟网络延迟
    await Future.delayed(const Duration(milliseconds: 250));
    
    // 按最后活跃时间排序
    final sortedContacts = List<ChatContact>.from(_contacts)
      ..sort((a, b) => b.lastActiveTime.compareTo(a.lastActiveTime));
    
    return sortedContacts.take(limit).toList();
  }

  @override
  Future<List<ChatContact>> getAgentContacts() async {
    // 模拟网络延迟
    await Future.delayed(const Duration(milliseconds: 150));
    return _contacts.where((contact) => contact.type == ChatContactType.agent).toList();
  }

  @override
  Future<List<ChatContact>> getDoctorContacts() async {
    // 模拟网络延迟
    await Future.delayed(const Duration(milliseconds: 150));
    return _contacts.where((contact) => contact.type == ChatContactType.doctor).toList();
  }

  @override
  Future<List<ChatContact>> getProviderContacts() async {
    // 模拟网络延迟
    await Future.delayed(const Duration(milliseconds: 150));
    return _contacts.where((contact) => contact.type == ChatContactType.provider).toList();
  }

  @override
  Future<List<ChatMessage>> getChatMessages(String contactId, {int limit = 20, int offset = 0}) async {
    // 模拟网络延迟
    await Future.delayed(const Duration(milliseconds: 350));
    
    final messages = _messages[contactId] ?? [];
    
    // 按发送时间排序（最新的在前）
    final sortedMessages = List<ChatMessage>.from(messages)
      ..sort((a, b) => b.sentTime.compareTo(a.sentTime));
    
    // 应用分页
    if (offset >= sortedMessages.length) {
      return [];
    }
    
    final end = (offset + limit) > sortedMessages.length 
      ? sortedMessages.length 
      : offset + limit;
    
    return sortedMessages.sublist(offset, end);
  }

  @override
  Future<ChatMessage> sendMessage(String contactId, String content, {ChatMessageType type = ChatMessageType.text}) async {
    // 模拟网络延迟
    await Future.delayed(const Duration(milliseconds: 400));
    
    final newMessage = ChatMessage(
      id: 'msg_${DateTime.now().millisecondsSinceEpoch}',
      senderId: 'current_user',
      receiverId: contactId,
      content: content,
      type: type,
      sentTime: DateTime.now(),
      isRead: false,
      status: ChatMessageStatus.sent,
    );
    
    // 添加消息到列表
    _messages.putIfAbsent(contactId, () => []);
    _messages[contactId]!.add(newMessage);
    
    // 更新联系人最后消息和时间
    final contactIndex = _contacts.indexWhere((c) => c.id == contactId);
    if (contactIndex != -1) {
      _contacts[contactIndex] = _contacts[contactIndex].copyWith(
        lastMessage: content,
        lastActiveTime: DateTime.now(),
      );
    }
    
    return newMessage;
  }

  @override
  Future<void> markMessagesAsRead(String contactId) async {
    // 模拟网络延迟
    await Future.delayed(const Duration(milliseconds: 200));
    
    // 获取联系人的所有消息
    final messages = _messages[contactId] ?? [];
    
    // 更新所有未读消息为已读
    _messages[contactId] = messages.map((message) {
      if (message.receiverId == 'current_user' && !message.isRead) {
        return ChatMessage(
          id: message.id,
          senderId: message.senderId,
          receiverId: message.receiverId,
          content: message.content,
          type: message.type,
          sentTime: message.sentTime,
          isRead: true,
          status: ChatMessageStatus.read,
          extraData: message.extraData,
        );
      }
      return message;
    }).toList();
    
    // 更新联系人未读消息数
    final contactIndex = _contacts.indexWhere((c) => c.id == contactId);
    if (contactIndex != -1) {
      _contacts[contactIndex] = _contacts[contactIndex].copyWith(
        unreadCount: 0,
      );
    }
  }

  @override
  Future<void> addContactToFavorites(String contactId) async {
    // 模拟网络延迟
    await Future.delayed(const Duration(milliseconds: 150));
    _favorites.add(contactId);
  }

  @override
  Future<void> removeContactFromFavorites(String contactId) async {
    // 模拟网络延迟
    await Future.delayed(const Duration(milliseconds: 150));
    _favorites.remove(contactId);
  }

  @override
  Future<List<ChatContact>> searchContacts(String query) async {
    // 模拟网络延迟
    await Future.delayed(const Duration(milliseconds: 300));
    
    if (query.isEmpty) {
      return [];
    }
    
    // 搜索联系人
    return _contacts.where((contact) {
      return contact.name.toLowerCase().contains(query.toLowerCase()) ||
             contact.description.toLowerCase().contains(query.toLowerCase());
    }).toList();
  }
}