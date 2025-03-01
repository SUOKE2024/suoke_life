import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// 网络信息接口
/// 用于检测设备的网络连接状态
abstract class NetworkInfo {
  /// 检查当前是否有网络连接
  Future<bool> get isConnected;
  
  /// 获取当前网络连接类型
  Future<ConnectivityResult> get connectionType;
  
  /// 监听网络状态变化的流
  Stream<ConnectivityResult> get onConnectivityChanged;
}

/// 网络信息实现类
class NetworkInfoImpl implements NetworkInfo {
  final Connectivity _connectivity;
  
  NetworkInfoImpl(this._connectivity);
  
  @override
  Future<bool> get isConnected async {
    final result = await _connectivity.checkConnectivity();
    return result != ConnectivityResult.none;
  }
  
  @override
  Future<ConnectivityResult> get connectionType async {
    return await _connectivity.checkConnectivity();
  }
  
  @override
  Stream<ConnectivityResult> get onConnectivityChanged {
    return _connectivity.onConnectivityChanged;
  }
}

/// 网络信息提供者
final networkInfoProvider = Provider<NetworkInfo>((ref) {
  return NetworkInfoImpl(Connectivity());
});

/// 网络连接状态提供者
final networkConnectedProvider = FutureProvider<bool>((ref) async {
  final networkInfo = ref.watch(networkInfoProvider);
  return networkInfo.isConnected;
});

/// 网络连接类型提供者
final connectionTypeProvider = StreamProvider<ConnectivityResult>((ref) {
  final networkInfo = ref.watch(networkInfoProvider);
  return networkInfo.onConnectivityChanged;
});