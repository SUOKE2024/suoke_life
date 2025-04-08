// mock classes for testing
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';
import 'package:suoke_life/data/datasources/user_remote_data_source.dart';
import 'package:suoke_life/domain/repositories/user_repository.dart';
import 'package:suoke_life/core/network/network_info.dart';
import 'package:suoke_life/domain/usecases/update_user_profile.dart';
import 'package:internet_connection_checker/internet_connection_checker.dart';
import 'package:http/http.dart' as http;

// 生成User服务测试所需的所有mock类
@GenerateMocks([
  UserRepository,
  UserRemoteDataSource,
  NetworkInfo,
  UpdateUserProfile,
  InternetConnectionChecker
], customMocks: [
  MockSpec<http.Client>(as: #MockClient),
])
void main() {} 