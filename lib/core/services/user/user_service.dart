import 'package:suoke_life/lib/core/models/user.dart';

abstract class UserService {
  Future<User?> getUser(String userId);
  Future<void> saveUser(User user);
} 