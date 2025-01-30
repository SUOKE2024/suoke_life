import 'package:json_annotation/json_annotation.dart';

part 'chat_info.g.dart';

@JsonSerializable()
class ChatInfo {
  final String id;
  final String title;
  final String? lastMessage;
  final DateTime? lastMessageTime;

  ChatInfo({
    required this.id,
    required this.title,
    this.lastMessage,
    this.lastMessageTime,
  });

  factory ChatInfo.fromJson(Map<String, dynamic> json) => 
      _$ChatInfoFromJson(json);

  Map<String, dynamic> toJson() => _$ChatInfoToJson(this);
} 