import 'package:json_annotation/json_annotation.dart';

part 'chat_info.g.dart';

@JsonSerializable()
class ChatInfo {
  final String id;
  final String name;
  final int unreadCount;
  final String? lastMessage;
  final DateTime? lastMessageTime;

  const ChatInfo({
    required this.id,
    required this.name,
    this.unreadCount = 0,
    this.lastMessage,
    this.lastMessageTime,
  });

  ChatInfo copyWith({
    String? id,
    String? name,
    int? unreadCount,
    String? lastMessage,
    DateTime? lastMessageTime,
  }) {
    return ChatInfo(
      id: id ?? this.id,
      name: name ?? this.name,
      unreadCount: unreadCount ?? this.unreadCount,
      lastMessage: lastMessage ?? this.lastMessage,
      lastMessageTime: lastMessageTime ?? this.lastMessageTime,
    );
  }

  factory ChatInfo.fromJson(Map<String, dynamic> json) => 
      _$ChatInfoFromJson(json);

  Map<String, dynamic> toJson() => _$ChatInfoToJson(this);

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is ChatInfo &&
          runtimeType == other.runtimeType &&
          id == other.id &&
          name == other.name &&
          unreadCount == other.unreadCount &&
          lastMessage == other.lastMessage &&
          lastMessageTime == other.lastMessageTime;

  @override
  int get hashCode =>
      id.hashCode ^
      name.hashCode ^
      unreadCount.hashCode ^
      lastMessage.hashCode ^
      lastMessageTime.hashCode;
} 