import 'package:suoke_life/core/models/user.dart';

abstract class UserRepository {
  Future<User> getUser(int id);
  Future<List<User>> getAllUsers();
  Future<User> addUser(User user);
  Future<User> updateUser(User user);
  Future<void> deleteUser(int id);
} 