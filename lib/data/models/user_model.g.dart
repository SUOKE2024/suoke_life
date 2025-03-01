// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'user_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

UserModel _$UserModelFromJson(Map<String, dynamic> json) => UserModel(
      id: json['id'] as String,
      username: json['username'] as String,
      email: json['email'] as String?,
      phone: json['phone'] as String?,
      avatarUrl: json['avatarUrl'] as String?,
      createdAt: (json['createdAt'] as num).toInt(),
      updatedAt: (json['updatedAt'] as num).toInt(),
      lastLogin: (json['lastLogin'] as num?)?.toInt(),
      accountType: json['accountType'] as String,
      syncStatus: json['sync_status'] as String? ?? 'pending',
    );

Map<String, dynamic> _$UserModelToJson(UserModel instance) => <String, dynamic>{
      'id': instance.id,
      'username': instance.username,
      'email': instance.email,
      'phone': instance.phone,
      'avatarUrl': instance.avatarUrl,
      'createdAt': instance.createdAt,
      'updatedAt': instance.updatedAt,
      'lastLogin': instance.lastLogin,
      'accountType': instance.accountType,
      'sync_status': instance.syncStatus,
    };
