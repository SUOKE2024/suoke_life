import 'package:mockito/annotations.dart';
import 'package:http/http.dart' as http;
import 'package:internet_connection_checker/internet_connection_checker.dart';
import 'package:suoke_life/data/datasources/auth_remote_data_source.dart';
import 'package:suoke_life/domain/repositories/auth_repository.dart';
import 'package:suoke_life/core/network/network_info.dart';

@GenerateMocks([
  AuthRepository,
  AuthRemoteDataSource,
  NetworkInfo,
  InternetConnectionChecker,
  http.Client,
])
void main() {} 