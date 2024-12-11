/// 安全配置
class SecurityConfig {
  /// 加密算法
  final String algorithm;
  
  /// 密钥长度
  final int keyLength;
  
  /// 是否启用安全存储
  final bool enableSecureStorage;
  
  /// 密钥轮换间隔
  final Duration keyRotationInterval;
  
  /// 完整性校验
  final bool enableIntegrityCheck;
  
  /// 安全擦除
  final bool enableSecureErase;

  const SecurityConfig({
    this.algorithm = 'AES',
    this.keyLength = 256,
    this.enableSecureStorage = true,
    this.keyRotationInterval = const Duration(days: 90),
    this.enableIntegrityCheck = true,
    this.enableSecureErase = true,
  });
} 