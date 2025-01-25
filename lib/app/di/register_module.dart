import 'package:injectable/injectable.dart';
import 'package:sqflite/sqflite.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

@module
abstract class RegisterModule {
  @singleton
  FlutterSecureStorage get secureStorage => const FlutterSecureStorage();
} 