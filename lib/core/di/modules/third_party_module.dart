import 'package:device_info_plus/device_info_plus.dart';
import 'package:injectable/injectable.dart';
import 'package:internet_connection_checker/internet_connection_checker.dart';
import 'package:local_auth/local_auth.dart';

@module
abstract class ThirdPartyModule {
  @singleton
  InternetConnectionChecker get connectionChecker => InternetConnectionChecker();

  @singleton
  LocalAuthentication get localAuth => LocalAuthentication();

  @singleton
  DeviceInfoPlugin get deviceInfo => DeviceInfoPlugin();
} 