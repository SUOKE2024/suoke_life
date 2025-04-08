import 'dart:convert';
import 'dart:math';
import 'dart:typed_data';

import 'package:crypto/crypto.dart';
import 'package:encrypt/encrypt.dart' as encrypt;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:suoke_life/core/models/sensor_data.dart';
import 'package:suoke_life/core/utils/logger.dart';
import 'package:uuid/uuid.dart';

part 'privacy_protection_service.g.dart';

/// 隐私保护服务提供者
@riverpod
PrivacyProtectionService privacyProtectionService(
    PrivacyProtectionServiceRef ref) {
  return PrivacyProtectionService();
}

/// 加密引擎
class EncryptionEngine {
  /// 密钥
  final List<int> _key;

  /// 初始化向量
  final List<int> _iv;

  /// 加密器
  late encrypt.Encrypter _encrypter;

  /// 初始化向量封装
  late encrypt.IV _initVector;

  /// 构造函数
  EncryptionEngine({
    required List<int> key,
    required List<int> iv,
  })  : _key = key,
        _iv = iv {
    // 创建密钥对象
    final encryptKey = encrypt.Key(Uint8List.fromList(_key));
    _initVector = encrypt.IV(Uint8List.fromList(_iv));

    // 创建AES加密器
    _encrypter = encrypt.Encrypter(encrypt.AES(
      encryptKey,
      mode: encrypt.AESMode.cbc, // 使用CBC模式增强安全性
      padding: 'PKCS7', // 使用PKCS7填充
    ));
  }

  /// 加密数据
  String encrypt(String data) {
    final encrypted = _encrypter.encrypt(data, iv: _initVector);
    return encrypted.base64;
  }

  /// 解密数据
  String decrypt(String encryptedData) {
    final encrypted = encrypt.Encrypted.fromBase64(encryptedData);
    return _encrypter.decrypt(encrypted, iv: _initVector);
  }
}

/// 差分隐私引擎
class DifferentialPrivacyEngine {
  /// 隐私预算 epsilon
  double _epsilon;

  /// 隐私参数 delta
  double _delta;

  /// 随机数生成器
  final _random = Random.secure();

  /// 构造函数
  DifferentialPrivacyEngine({
    required double epsilon,
    required double delta,
  })  : _epsilon = epsilon,
        _delta = delta;

  /// 更新参数
  void updateParameters({
    required double epsilon,
    required double delta,
  }) {
    _epsilon = epsilon;
    _delta = delta;
  }

  /// 添加拉普拉斯噪声
  double addLaplaceNoise(double value, double budget) {
    // 根据隐私预算调整噪声规模
    final scale = 1.0 / (budget * _epsilon);

    // 生成拉普拉斯分布噪声
    final u = _random.nextDouble() - 0.5;
    final noise = -scale * _sign(u) * log(1 - 2 * u.abs());

    return value + noise;
  }

  /// 添加高斯噪声
  double addGaussianNoise(double value, double budget) {
    final variance = 2.0 * log(1.25 / _delta) / (budget * _epsilon);
    final stdDev = sqrt(variance);

    // 生成标准正态分布噪声
    final u1 = _random.nextDouble();
    final u2 = _random.nextDouble();

    // Box-Muller变换
    final z = sqrt(-2.0 * log(u1)) * cos(2.0 * pi * u2);
    final noise = z * stdDev;

    return value + noise;
  }

  /// 对数值集合应用差分隐私
  List<double> applyToBatch(List<double> values, double budget) {
    return values.map((v) => addLaplaceNoise(v, budget)).toList();
  }

  /// 符号函数
  double _sign(double x) {
    if (x > 0) return 1.0;
    if (x < 0) return -1.0;
    return 0.0;
  }
}

/// 隐私预算
class PrivacyBudget {
  /// 总预算
  final double total;

  /// 字段预算分配
  final Map<String, double> fieldAllocations;

  /// 构造函数
  PrivacyBudget({
    required this.total,
    required this.fieldAllocations,
  });

  /// 获取字段预算
  double getBudgetForField(String field) {
    return fieldAllocations[field] ?? (total / fieldAllocations.length);
  }
}

/// 隐私设置
class PrivacySettings {
  /// 差分隐私epsilon参数
  final double differentialPrivacyEpsilon;

  /// 差分隐私delta参数
  final double differentialPrivacyDelta;

  /// 匿名化盐值
  final String anonymizationSalt;

  /// 敏感字段列表
  final List<String> sensitiveFields;

  /// 是否启用匿名化
  final bool enableAnonymization;

  /// 是否启用差分隐私
  final bool enableDifferentialPrivacy;

  /// 是否启用完全加密
  final bool enableFullEncryption;

  /// 构造函数
  PrivacySettings({
    required this.differentialPrivacyEpsilon,
    required this.differentialPrivacyDelta,
    required this.anonymizationSalt,
    required this.sensitiveFields,
    required this.enableAnonymization,
    required this.enableDifferentialPrivacy,
    required this.enableFullEncryption,
  });

  /// 默认设置
  factory PrivacySettings.defaults() {
    return PrivacySettings(
      differentialPrivacyEpsilon: 0.1,
      differentialPrivacyDelta: 0.001,
      anonymizationSalt: const Uuid().v4(), // 随机生成盐值
      sensitiveFields: [
        'userId',
        'deviceId',
        'location',
        'name',
        'email',
        'phoneNumber',
        'birthDate',
        'address',
        'healthData',
      ],
      enableAnonymization: true,
      enableDifferentialPrivacy: true,
      enableFullEncryption: false,
    );
  }

  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'differentialPrivacyEpsilon': differentialPrivacyEpsilon,
      'differentialPrivacyDelta': differentialPrivacyDelta,
      'anonymizationSalt': anonymizationSalt,
      'sensitiveFields': sensitiveFields,
      'enableAnonymization': enableAnonymization,
      'enableDifferentialPrivacy': enableDifferentialPrivacy,
      'enableFullEncryption': enableFullEncryption,
    };
  }

  /// 从JSON创建
  factory PrivacySettings.fromJson(Map<String, dynamic> json) {
    return PrivacySettings(
      differentialPrivacyEpsilon: json['differentialPrivacyEpsilon'] ?? 0.1,
      differentialPrivacyDelta: json['differentialPrivacyDelta'] ?? 0.001,
      anonymizationSalt: json['anonymizationSalt'] ?? const Uuid().v4(),
      sensitiveFields: List<String>.from(json['sensitiveFields'] ?? []),
      enableAnonymization: json['enableAnonymization'] ?? true,
      enableDifferentialPrivacy: json['enableDifferentialPrivacy'] ?? true,
      enableFullEncryption: json['enableFullEncryption'] ?? false,
    );
  }
}

/// 隐私保护服务
class PrivacyProtectionService {
  static const String _tag = 'PrivacyProtectionService';

  /// 安全存储
  final FlutterSecureStorage _secureStorage = const FlutterSecureStorage();

  /// 加密引擎
  late EncryptionEngine _encryptionEngine;

  /// 差分隐私引擎
  late DifferentialPrivacyEngine _dpEngine;

  /// 隐私设置
  late PrivacySettings _settings;

  /// 是否初始化完成
  bool _initialized = false;

  /// 初始化
  Future<void> initialize() async {
    Logger.i(_tag, '初始化隐私保护服务');

    try {
      // 加载隐私设置
      await _loadPrivacySettings();

      // 初始化加密引擎
      await _initEncryptionEngine();

      // 初始化差分隐私引擎
      _dpEngine = DifferentialPrivacyEngine(
        epsilon: _settings.differentialPrivacyEpsilon,
        delta: _settings.differentialPrivacyDelta,
      );

      _initialized = true;
      Logger.i(_tag, '隐私保护服务初始化完成');
    } catch (e) {
      Logger.e(_tag, '隐私保护服务初始化失败: $e');
    }
  }

  /// 加载隐私设置
  Future<void> _loadPrivacySettings() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final settingsJson = prefs.getString('privacy_settings');

      if (settingsJson != null) {
        _settings = PrivacySettings.fromJson(jsonDecode(settingsJson));
        Logger.d(_tag, '已加载隐私设置');
      } else {
        // 默认设置
        _settings = PrivacySettings.defaults();
        // 保存默认设置
        await prefs.setString(
            'privacy_settings', jsonEncode(_settings.toJson()));
        Logger.d(_tag, '使用默认隐私设置');
      }
    } catch (e) {
      Logger.e(_tag, '加载隐私设置失败: $e');
      _settings = PrivacySettings.defaults();
    }
  }

  /// 初始化加密引擎
  Future<void> _initEncryptionEngine() async {
    try {
      // 检查是否有现有密钥
      final hasKeys = await _checkEncryptionKeys();

      if (!hasKeys) {
        // 生成新密钥
        await _generateEncryptionKeys();
      }

      // 加载密钥
      final key = await _secureStorage.read(key: 'encryption_key');
      final iv = await _secureStorage.read(key: 'encryption_iv');

      if (key == null || iv == null) {
        throw Exception('加密密钥不存在');
      }

      // 初始化加密引擎
      _encryptionEngine = EncryptionEngine(
        key: base64.decode(key),
        iv: base64.decode(iv),
      );

      Logger.d(_tag, '加密引擎初始化完成');
    } catch (e) {
      Logger.e(_tag, '初始化加密引擎失败: $e');
      throw Exception('初始化加密引擎失败');
    }
  }

  /// 检查加密密钥
  Future<bool> _checkEncryptionKeys() async {
    final key = await _secureStorage.read(key: 'encryption_key');
    final iv = await _secureStorage.read(key: 'encryption_iv');

    return key != null && iv != null;
  }

  /// 生成加密密钥
  Future<void> _generateEncryptionKeys() async {
    try {
      // 生成随机密钥
      final key = encrypt.Key.fromSecureRandom(32);
      final iv = encrypt.IV.fromSecureRandom(16);

      // 安全存储
      await _secureStorage.write(
        key: 'encryption_key',
        value: base64.encode(key.bytes),
      );

      await _secureStorage.write(
        key: 'encryption_iv',
        value: base64.encode(iv.bytes),
      );

      Logger.d(_tag, '已生成新的加密密钥');
    } catch (e) {
      Logger.e(_tag, '生成加密密钥失败: $e');
      throw Exception('生成加密密钥失败');
    }
  }

  /// 确保服务已初始化
  void _ensureInitialized() {
    if (!_initialized) {
      throw Exception('隐私保护服务尚未初始化');
    }
  }

  /// 加密敏感数据
  Future<String> encryptData(String data) async {
    _ensureInitialized();

    try {
      return _encryptionEngine.encrypt(data);
    } catch (e) {
      Logger.e(_tag, '加密数据失败: $e');
      throw Exception('加密数据失败');
    }
  }

  /// 解密数据
  Future<String> decryptData(String encryptedData) async {
    _ensureInitialized();

    try {
      return _encryptionEngine.decrypt(encryptedData);
    } catch (e) {
      Logger.e(_tag, '解密数据失败: $e');
      throw Exception('解密数据失败');
    }
  }

  /// 应用差分隐私
  Future<Map<String, dynamic>> applyDifferentialPrivacy(
    Map<String, dynamic> data,
    PrivacyBudget budget,
  ) async {
    _ensureInitialized();

    // 如果未启用差分隐私，直接返回原始数据
    if (!_settings.enableDifferentialPrivacy) {
      return data;
    }

    try {
      // 对不同字段应用不同的隐私预算
      final result = Map<String, dynamic>.from(data);

      // 遍历敏感字段
      for (final field in _settings.sensitiveFields) {
        if (data.containsKey(field)) {
          // 根据字段类型应用相应的差分隐私
          if (data[field] is num) {
            // 数值型数据
            result[field] = _dpEngine.addLaplaceNoise(
              (data[field] as num).toDouble(),
              budget.getBudgetForField(field),
            );
          } else if (data[field] is String) {
            // 文本数据
            result[field] = await _anonymizeText(
              data[field] as String,
              budget.getBudgetForField(field),
            );
          } else if (data[field] is List) {
            // 列表数据 - 处理数值列表
            if (data[field] is List<num>) {
              result[field] = _dpEngine.applyToBatch(
                (data[field] as List<num>).map((e) => e.toDouble()).toList(),
                budget.getBudgetForField(field),
              );
            }
          } else if (data[field] is Map) {
            // 嵌套对象 - 递归处理
            result[field] = await applyDifferentialPrivacy(
              Map<String, dynamic>.from(data[field] as Map),
              PrivacyBudget(
                total: budget.getBudgetForField(field),
                fieldAllocations: {},
              ),
            );
          }
        }
      }

      return result;
    } catch (e) {
      Logger.e(_tag, '应用差分隐私失败: $e');
      // 失败时返回原始数据
      return data;
    }
  }

  /// 匿名化文本
  Future<String> _anonymizeText(String text, double budget) async {
    // 实现文本匿名化逻辑
    // 简单实现：用哈希替换文本，仅保留前几个字符作为标识
    try {
      final hash =
          sha256.convert(utf8.encode(text + _settings.anonymizationSalt));
      return text.length > 3
          ? '${text.substring(0, 2)}***${hash.toString().substring(0, 6)}'
          : '***${hash.toString().substring(0, 6)}';
    } catch (e) {
      Logger.e(_tag, '匿名化文本失败: $e');
      return '***';
    }
  }

  /// 对健康数据进行脱敏处理
  Future<Map<String, dynamic>> anonymizeHealthData(
      Map<String, dynamic> healthData) async {
    _ensureInitialized();

    if (!_settings.enableAnonymization) {
      return healthData;
    }

    try {
      final result = Map<String, dynamic>.from(healthData);

      // 标识符处理
      if (result.containsKey('userId')) {
        result['userId'] = _hashIdentifier(result['userId'] as String);
      }

      if (result.containsKey('deviceId')) {
        result['deviceId'] = _hashIdentifier(result['deviceId'] as String);
      }

      // 时间模糊化
      if (result.containsKey('timestamp') && result['timestamp'] is String) {
        result['timestamp'] =
            _generalizeTimestamp(result['timestamp'] as String);
      }

      // 位置模糊化
      if (result.containsKey('location') && result['location'] is Map) {
        result['location'] = _generalizeLocation(
            Map<String, dynamic>.from(result['location'] as Map));
      }

      // 处理传感器数据
      if (result.containsKey('sensorData') && result['sensorData'] is List) {
        result['sensorData'] =
            await _anonymizeSensorData(result['sensorData'] as List);
      }

      return result;
    } catch (e) {
      Logger.e(_tag, '匿名化健康数据失败: $e');
      // 失败时返回原始数据
      return healthData;
    }
  }

  /// 匿名化传感器数据
  Future<List<dynamic>> _anonymizeSensorData(List<dynamic> sensorData) async {
    final List<dynamic> result = [];

    for (final data in sensorData) {
      if (data is Map) {
        final Map<String, dynamic> anonymizedData =
            Map<String, dynamic>.from(data);

        // 处理时间戳
        if (anonymizedData.containsKey('timestamp') &&
            anonymizedData['timestamp'] is String) {
          anonymizedData['timestamp'] =
              _generalizeTimestamp(anonymizedData['timestamp'] as String);
        }

        // 处理用户ID
        if (anonymizedData.containsKey('userId') &&
            anonymizedData['userId'] is String) {
          anonymizedData['userId'] =
              _hashIdentifier(anonymizedData['userId'] as String);
        }

        // 处理设备ID
        if (anonymizedData.containsKey('deviceId') &&
            anonymizedData['deviceId'] is String) {
          anonymizedData['deviceId'] =
              _hashIdentifier(anonymizedData['deviceId'] as String);
        }

        result.add(anonymizedData);
      } else {
        result.add(data);
      }
    }

    return result;
  }

  /// 哈希标识符
  String _hashIdentifier(String identifier) {
    final bytes = utf8.encode(identifier + _settings.anonymizationSalt);
    final digest = sha256.convert(bytes);
    return digest.toString();
  }

  /// 模糊化时间戳
  String _generalizeTimestamp(String timestamp) {
    try {
      final date = DateTime.parse(timestamp);
      // 舍入到小时级别
      final generalizedDate = DateTime(
        date.year,
        date.month,
        date.day,
        date.hour,
      );
      return generalizedDate.toIso8601String();
    } catch (e) {
      Logger.e(_tag, '模糊化时间戳失败: $e');
      return timestamp;
    }
  }

  /// 模糊化位置
  Map<String, dynamic> _generalizeLocation(Map<String, dynamic> location) {
    final result = Map<String, dynamic>.from(location);

    // 减少位置精度
    if (result.containsKey('latitude') && result.containsKey('longitude')) {
      // 保留到小数点后两位（约1.1公里精度）
      if (result['latitude'] is num) {
        result['latitude'] = (result['latitude'] as num).toDouble();
        result['latitude'] = (result['latitude'] * 100).round() / 100;
      }

      if (result['longitude'] is num) {
        result['longitude'] = (result['longitude'] as num).toDouble();
        result['longitude'] = (result['longitude'] * 100).round() / 100;
      }
    }

    return result;
  }

  /// 更新隐私设置
  Future<void> updatePrivacySettings(PrivacySettings newSettings) async {
    _ensureInitialized();

    try {
      _settings = newSettings;

      // 保存新设置
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('privacy_settings', jsonEncode(_settings.toJson()));

      // 更新差分隐私引擎参数
      _dpEngine.updateParameters(
        epsilon: _settings.differentialPrivacyEpsilon,
        delta: _settings.differentialPrivacyDelta,
      );

      Logger.i(_tag, '已更新隐私设置');
    } catch (e) {
      Logger.e(_tag, '更新隐私设置失败: $e');
      throw Exception('更新隐私设置失败');
    }
  }

  /// 获取当前隐私设置
  PrivacySettings getPrivacySettings() {
    _ensureInitialized();
    return _settings;
  }

  /// 应用隐私保护处理传感器数据
  Future<List<SensorReading>> protectSensorData(
      List<SensorReading> readings) async {
    _ensureInitialized();

    if (!_settings.enableAnonymization &&
        !_settings.enableDifferentialPrivacy) {
      return readings;
    }

    try {
      final result = <SensorReading>[];

      for (final reading in readings) {
        var values = List<double>.from(reading.values);

        // 应用差分隐私
        if (_settings.enableDifferentialPrivacy) {
          values = _dpEngine.applyToBatch(
            values,
            0.1, // 固定预算分配
          );
        }

        // 创建新的读取对象
        final protectedReading = SensorReading(
          type: reading.type,
          values: values,
          timestamp: reading.timestamp,
          // 模糊化或删除元数据
          metadata: reading.metadata != null
              ? await anonymizeHealthData(reading.metadata!)
              : null,
        );

        result.add(protectedReading);
      }

      return result;
    } catch (e) {
      Logger.e(_tag, '保护传感器数据失败: $e');
      // 失败时返回原始数据
      return readings;
    }
  }

  /// 检查删除过期数据
  Future<void> cleanupExpiredData() async {
    _ensureInitialized();

    // TODO: 实现过期数据清理逻辑
  }
}
