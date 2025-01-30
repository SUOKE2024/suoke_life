import 'package:suoke_life/lib/core/models/user.dart';

abstract class AuthRepository {
  Future<User?> login(String username, String password);
  Future<void> logout();
  Future<User?> getCurrentUser();
  Future<void> updateUserProfile(User user);
}
