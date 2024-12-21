import 'package:get/get.dart';
import 'package:shared_preferences/shared_preferences.dart';

class AuthService extends GetxService {
  static const _tokenKey = 'auth_token';
  static const _userIdKey = 'user_id';
  
  final _prefs = Get.find<SharedPreferences>();
  final _token = Rx<String?>(null);
  final _userId = Rx<String?>(null);

  String? get token => _token.value;
  String? get userId => _userId.value;
  bool get isAuthenticated => token != null;

  @override
  void onInit() {
    super.onInit();
    _loadAuthData();
  }

  void _loadAuthData() {
    _token.value = _prefs.getString(_tokenKey);
    _userId.value = _prefs.getString(_userIdKey);
  }

  Future<void> saveToken(String token) async {
    await _prefs.setString(_tokenKey, token);
    _token.value = token;
  }

  Future<void> saveUserId(String userId) async {
    await _prefs.setString(_userIdKey, userId);
    _userId.value = userId;
  }

  Future<void> login(String token, String userId) async {
    await saveToken(token);
    await saveUserId(userId);
  }

  Future<void> logout() async {
    await _prefs.remove(_tokenKey);
    await _prefs.remove(_userIdKey);
    _token.value = null;
    _userId.value = null;
  }

  Future<void> clearAuthData() async {
    await _prefs.remove(_tokenKey);
    await _prefs.remove(_userIdKey);
    _token.value = null;
    _userId.value = null;
  }
} 