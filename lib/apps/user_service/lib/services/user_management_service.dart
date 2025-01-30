import 'package:suoke_life/lib/core/network/user_service_client.dart';

class UserManagementService {
  final UserServiceClient _userServiceClient;

  UserManagementService(this._userServiceClient);

  Future<String> getUserProfile(String userId) async {
    final response = await _userServiceClient.getUserProfile(userId);
    return 'User profile: ${response.data}';
  }
} 