import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';
import 'package:suoke_life/core/network/network_info.dart';
import 'package:suoke_life/core/utils/secure_storage.dart';
import 'package:suoke_life/data/datasources/auth_remote_data_source.dart';
import 'package:suoke_life/domain/repositories/auth_repository.dart';

@GenerateMocks([
  AuthRemoteDataSource,
  NetworkInfo,
  SecureStorage,
  AuthRepository,
])
void main() {} 