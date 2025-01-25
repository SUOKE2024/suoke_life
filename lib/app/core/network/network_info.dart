import 'package:injectable/injectable.dart';
import 'package:internet_connection_checker/internet_connection_checker.dart';

@singleton
class NetworkInfoImpl {
  final InternetConnectionChecker connectionChecker;

  NetworkInfoImpl(this.connectionChecker);
  
  // ... rest of implementation
} 