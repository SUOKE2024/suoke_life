import 'package:suoke_life/core/models/user.dart';
import 'package:suoke_life/core/services/network_service.dart';

class UserServiceClient {
  final NetworkService _networkService;

  UserServiceClient(this._networkService);

  Future<User> getUser(int id) async {
    final response = await _networkService.get('/users/$id');
    return User.fromJson(response);
  }

  Future<List<User>> getAllUsers() async {
    final response = await _networkService.get('/users');
    if (response is List) {
      return response.map((e) => User.fromJson(e)).toList();
    } else {
      throw Exception('Invalid response format');
    }
  }

  Future<User> addUser(User user) async {
    final response = await _networkService.post('/users', user.toJson());
    return User.fromJson(response);
  }

  Future<User> updateUser(User user) async {
    final response = await _networkService.put('/users/${user.id}', user.toJson());
    return User.fromJson(response);
  }

  Future<void> deleteUser(int id) async {
    await _networkService.delete('/users/$id');
  }
} 