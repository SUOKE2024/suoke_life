/// 聊天联系人模型
class ChatContact {
  /// 联系人ID
  final String id;
  
  /// 联系人名称
  final String name;
  
  /// 联系人类型
  final ChatContactType type;
  
  /// 头像URL
  final String avatarUrl;
  
  /// 简介描述
  final String description;
  
  /// 最后一条消息内容
  final String? lastMessage;
  
  /// 最后消息时间
  final DateTime lastActiveTime;
  
  /// 未读消息数
  final int unreadCount;
  
  /// 验证状态（用于供应商）
  final VerificationStatus verificationStatus;
  
  /// 附加数据
  final Map<String, dynamic>? extraData;

  /// 构造函数
  ChatContact({
    required this.id,
    required this.name,
    required this.type,
    required this.avatarUrl,
    required this.description,
    this.lastMessage,
    required this.lastActiveTime,
    this.unreadCount = 0,
    this.verificationStatus = VerificationStatus.verified,
    this.extraData,
  });
  
  /// 复制并修改
  ChatContact copyWith({
    String? id,
    String? name,
    ChatContactType? type,
    String? avatarUrl,
    String? description,
    String? lastMessage,
    DateTime? lastActiveTime,
    int? unreadCount,
    VerificationStatus? verificationStatus,
    Map<String, dynamic>? extraData,
  }) {
    return ChatContact(
      id: id ?? this.id,
      name: name ?? this.name,
      type: type ?? this.type,
      avatarUrl: avatarUrl ?? this.avatarUrl,
      description: description ?? this.description,
      lastMessage: lastMessage ?? this.lastMessage,
      lastActiveTime: lastActiveTime ?? this.lastActiveTime,
      unreadCount: unreadCount ?? this.unreadCount,
      verificationStatus: verificationStatus ?? this.verificationStatus,
      extraData: extraData ?? this.extraData,
    );
  }
}

/// 联系人类型
enum ChatContactType {
  /// 智能体
  agent,
  
  /// 名医
  doctor,
  
  /// 用户
  user,
  
  /// 供应商
  provider,
}

/// 验证状态
enum VerificationStatus {
  /// 待审核
  pending,
  
  /// 已验证
  verified,
  
  /// 未验证
  unverified,
  
  /// 已拒绝
  rejected,
} 