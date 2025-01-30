import 'package:injectable/injectable.dart';

@singleton
class SecurityConfig {
  final int keyRotationDays;
  final String encryptionAlgorithm;
  final int keyLength;
  final String hashAlgorithm;

  const SecurityConfig({
    this.keyRotationDays = 30,
    this.encryptionAlgorithm = 'AES-256-GCM',
    this.keyLength = 256,
    this.hashAlgorithm = 'SHA-256',
  });
} 