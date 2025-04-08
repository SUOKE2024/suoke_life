import 'package:mockito/annotations.dart';
import 'package:http/http.dart' as http;
import 'package:internet_connection_checker/internet_connection_checker.dart';
import 'package:suoke_life/data/datasources/user_remote_data_source.dart';
import 'package:suoke_life/domain/repositories/user_repository.dart';
import 'package:suoke_life/domain/usecases/update_user_profile.dart';
import 'package:suoke_life/core/network/network_info.dart';

@GenerateMocks([
  UserRepository,
  UserRemoteDataSource,
  NetworkInfo,
  UpdateUserProfile,
  InternetConnectionChecker,
  http.Client,
])
void main() {} 