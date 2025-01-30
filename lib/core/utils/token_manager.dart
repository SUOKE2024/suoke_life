import 'package:shared_preferences/shared_preferences.dart';

class TokenManager {
  static const String _tokenKey = 'auth_token';
  static const String _refreshTokenKey = 'refresh_token';
  
  final SharedPreferences _prefs;

  TokenManager(this._prefs);

  Future<String?> getToken() async {
    return _prefs.getString(_tokenKey);
  }

  Future<void> setToken(String token) async {
    await _prefs.setString(_tokenKey, token);
  }

  Future<String?> getRefreshToken() async {
    return _prefs.getString(_refreshTokenKey);
  }

  Future<void> setRefreshToken(String token) async {
    await _prefs.setString(_refreshTokenKey, token);
  }

  Future<void> clearTokens() async {
    await _prefs.remove(_tokenKey);
    await _prefs.remove(_refreshTokenKey);
  }

  Future<bool> refreshToken() async {
    try {
      final refreshToken = await getRefreshToken();
      if (refreshToken == null) return false;

      // TODO: 调用刷新token的API
      // final response = await _apiClient.post('/auth/refresh', data: {
      //   'refresh_token': refreshToken,
      // });
      
      // await setToken(response['token']);
      // await setRefreshToken(response['refresh_token']);
      
      return true;
    } catch (e) {
      await clearTokens();
      return false;
    }
  }
} 