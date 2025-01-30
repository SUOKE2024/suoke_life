import 'dart:convert';
import 'package:crypto/crypto.dart';

class AnonymizerService {
  String anonymizeUserId(String id) {
    return sha256.convert(utf8.encode(id)).toString().substring(0, 8);
  }

  Map<String, dynamic> anonymizeUserData(Map<String, dynamic> data) {
    return {
      'id': anonymizeUserId(data['id']),
      'city': data['city'],
      'province': data['province'],
      'country': data['country'],
    };
  }

  Map<String, dynamic> anonymizeDeviceInfo(Map<String, dynamic> device) {
    return {
      'platform': device['platform'],
      'version': device['version'],
    };
  }
} 