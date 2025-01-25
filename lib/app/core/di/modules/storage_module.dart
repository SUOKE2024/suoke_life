import 'package:injectable/injectable.dart';
import 'package:shared_preferences/shared_preferences.dart';

@module
abstract class StorageModule {
  @factoryMethod
  Future<SharedPreferences> createPrefs() => SharedPreferences.getInstance();
} 