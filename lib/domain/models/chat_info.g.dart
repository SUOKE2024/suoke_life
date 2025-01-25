// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'chat_info.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

ChatInfo _$ChatInfoFromJson(Map<String, dynamic> json) => ChatInfo(
      id: json['id'] as String,
      name: json['name'] as String,
      unreadCount: (json['unreadCount'] as num?)?.toInt() ?? 0,
      lastMessage: json['lastMessage'] as String?,
      lastMessageTime: json['lastMessageTime'] == null
          ? null
          : DateTime.parse(json['lastMessageTime'] as String),
    );

Map<String, dynamic> _$ChatInfoToJson(ChatInfo instance) => <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'unreadCount': instance.unreadCount,
      'lastMessage': instance.lastMessage,
      'lastMessageTime': instance.lastMessageTime?.toIso8601String(),
    };
