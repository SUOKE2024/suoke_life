// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'login_log.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

LoginLog _$LoginLogFromJson(Map<String, dynamic> json) => LoginLog(
      id: json['id'] as String,
      userId: json['userId'] as String,
      loginType: json['loginType'] as String,
      deviceInfo: json['deviceInfo'] as String,
      ipAddress: json['ipAddress'] as String,
      location: json['location'] as String,
      isSuccess: json['isSuccess'] as bool,
      failureReason: json['failureReason'] as String?,
      createdAt: DateTime.parse(json['createdAt'] as String),
    );

Map<String, dynamic> _$LoginLogToJson(LoginLog instance) => <String, dynamic>{
      'id': instance.id,
      'userId': instance.userId,
      'loginType': instance.loginType,
      'deviceInfo': instance.deviceInfo,
      'ipAddress': instance.ipAddress,
      'location': instance.location,
      'isSuccess': instance.isSuccess,
      'failureReason': instance.failureReason,
      'createdAt': instance.createdAt.toIso8601String(),
    };
