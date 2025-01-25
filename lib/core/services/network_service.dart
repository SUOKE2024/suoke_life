abstract class NetworkService {
  Future<dynamic> get(String path);
  Future<dynamic> post(String path, dynamic data);
  Future<dynamic> put(String path, dynamic data);
  Future<dynamic> delete(String path);
} 