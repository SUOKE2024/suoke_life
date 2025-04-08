import 'package:mockito/annotations.dart';
import 'package:suoke_life/core/network/api_client.dart';
import 'package:suoke_life/core/network/network_info.dart';
import 'package:suoke_life/data/datasources/remote/laoke_remote_datasource.dart';
import 'package:suoke_life/domain/repositories/laoke_repository.dart';
import 'package:suoke_life/core/storage/secure_storage.dart';

@GenerateMocks([
  ApiClient,
  NetworkInfo,
  LaokeRemoteDataSource,
  LaokeRepository,
  SecureStorage,
])
void main() {} 