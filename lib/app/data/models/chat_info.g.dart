// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'chat_info.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

ChatInfo _$ChatInfoFromJson(Map<String, dynamic> json) => ChatInfo(
      id: json['id'] as String,
      title: json['title'] as String,
      lastMessage: json['lastMessage'] as String?,
      lastMessageTime: json['lastMessageTime'] == null
          ? null
          : DateTime.parse(json['lastMessageTime'] as String),
    );

Map<String, dynamic> _$ChatInfoToJson(ChatInfo instance) => <String, dynamic>{
      'id': instance.id,
      'title': instance.title,
      'lastMessage': instance.lastMessage,
      'lastMessageTime': instance.lastMessageTime?.toIso8601String(),
    };
