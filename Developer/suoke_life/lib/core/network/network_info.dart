import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:internet_connection_checker/internet_connection_checker.dart';

/// 网络信息接口
///
/// 提供网络连接状态检查功能
abstract class NetworkInfo {
  /// 检查是否有网络连接
  Future<bool> get isConnected;

  /// 检查是否通过Wi-Fi连接
  Future<bool> get isWifi;

  /// 检查是否通过移动网络连接
  Future<bool> get isMobile;
}

/// 网络信息实现类
class NetworkInfoImpl implements NetworkInfo {
  final Connectivity _connectivity;
  final InternetConnectionChecker connectionChecker;

  /// 创建网络信息实现
  NetworkInfoImpl(this._connectivity, this.connectionChecker);

  @override
  Future<bool> get isConnected => connectionChecker.hasConnection;

  @override
  Future<bool> get isWifi async {
    final result = await _connectivity.checkConnectivity();
    return result == ConnectivityResult.wifi;
  }

  @override
  Future<bool> get isMobile async {
    final result = await _connectivity.checkConnectivity();
    return result == ConnectivityResult.mobile;
  }
}

/// 网络信息Provider
final networkInfoProvider = Provider<NetworkInfo>((ref) {
  return NetworkInfoImpl(Connectivity(), InternetConnectionChecker());
}); 