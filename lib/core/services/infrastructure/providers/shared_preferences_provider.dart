import 'package:shared_preferences/shared_preferences.dart';

class SharedPreferencesProvider {
  static late SharedPreferences _prefs;

  static Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
  }

  static SharedPreferences get prefs => _prefs;
} 