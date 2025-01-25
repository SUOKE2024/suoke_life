import 'package:injectable/injectable.dart';
import 'package:suoke_life/core/network/user_service_client.dart';

@injectable
class UserManagementService {
  final UserServiceClient _userServiceClient;

  UserManagementService(this._userServiceClient);

  Future<String> getUserProfile(String userId) async {
    final response = await _userServiceClient.getUserProfile(userId);
    return 'User profile: ${response.data}';
  }
} 