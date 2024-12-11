import 'package:flutter_dotenv/flutter_dotenv.dart';

class EnvConfig {
  static String get amapIosKey => dotenv.env['AMAP_IOS_KEY'] ?? '';
  static String get amapAndroidKey => dotenv.env['AMAP_ANDROID_KEY'] ?? '';
  
  static Future<void> load() async {
    await dotenv.load(fileName: '.env');
  }
} 