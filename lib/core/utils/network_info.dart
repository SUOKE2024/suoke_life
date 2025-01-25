import 'package:connectivity_plus/connectivity_plus.dart';

class NetworkInfo {
  final Connectivity connectivity = Connectivity();

  Future<bool> get isConnected async {
    final connectivityResult = await connectivity.checkConnectivity();
    return connectivityResult != ConnectivityResult.none;
  }
} 