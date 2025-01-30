import 'package:sqflite/sqflite.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

abstract class RegisterModule {
  FlutterSecureStorage get secureStorage => const FlutterSecureStorage();
} 