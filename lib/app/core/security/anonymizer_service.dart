import 'package:injectable/injectable.dart';
import 'dart:convert';
import 'package:crypto/crypto.dart';

@singleton
class AnonymizerService {
  String anonymizeUserId(String userId) {
    final bytes = utf8.encode(userId);
    final digest = sha256.convert(bytes);
    return digest.toString();
  }

  String anonymizeLocation(String location) {
    // 只保留城市级别
    final parts = location.split(',');
    if (parts.length > 1) {
      return parts[1].trim();
    }
    return location;
  }

  Map<String, dynamic> anonymizeDeviceInfo(Map<String, dynamic> deviceInfo) {
    return {
      'platform': deviceInfo['platform'],
      'version': deviceInfo['version'],
    };
  }

  Map<String, dynamic> anonymizeUserData(Map<String, dynamic> userData) {
    return {
      'id': anonymizeUserId(userData['id']),
      'location': anonymizeLocation(userData['location'] ?? ''),
      'device': anonymizeDeviceInfo(userData['device'] ?? {}),
      'timestamp': DateTime.now().millisecondsSinceEpoch,
    };
  }
} 