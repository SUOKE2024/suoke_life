import 'package:injectable/injectable.dart';
import '../../../core/database/database_service.dart';
import '../../../core/network/network_service.dart';
import '../../../core/security/encryption_service.dart';
import '../../../data/models/user.dart';

@singleton
class UserService {
  final DatabaseService _db;
  final NetworkService _network;
  final EncryptionService _encryption;

  UserService(this._db, this._network, this._encryption);

  Future<User?> getCurrentUser() async {
    final localUser = await _db.getUserData('current_user');
    if (localUser != null) {
      return User.fromMap(localUser);
    }
    return null;
  }

  Future<void> updateProfile(Map<String, dynamic> data) async {
    await _db.saveUserData('current_user', data);
    // 同步到远程
    await _network.post('/user/profile', data, encrypt: true);
  }
} 