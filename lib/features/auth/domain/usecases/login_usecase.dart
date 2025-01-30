import 'package:suoke_life/lib/core/models/user.dart';
import 'package:suoke_life/features/auth/domain/repositories/auth_repository.dart';

class LoginUseCase {
  final AuthRepository repository;

  LoginUseCase(this.repository);

  Future<User?> execute(String username, String password) async {
    return await repository.login(username, password);
  }
}
