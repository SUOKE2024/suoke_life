/// 网络服务接口
abstract class NetworkService extends BaseService {
  /// 发送 GET 请求
  Future<Response> get(
    String path, {
    Map<String, dynamic>? params,
    Map<String, String>? headers,
    Duration? timeout,
  });

  /// 发送 POST 请求
  Future<Response> post(
    String path, {
    dynamic data,
    Map<String, String>? headers,
    Duration? timeout,
  });

  /// 发送 PUT 请求
  Future<Response> put(
    String path, {
    dynamic data,
    Map<String, String>? headers,
    Duration? timeout,
  });

  /// 发送 DELETE 请求
  Future<Response> delete(
    String path, {
    Map<String, dynamic>? params,
    Map<String, String>? headers,
    Duration? timeout,
  });

  /// 上传文件
  Future<Response> upload(
    String path,
    List<MultipartFile> files, {
    Map<String, dynamic>? data,
    Map<String, String>? headers,
    ProgressCallback? onProgress,
  });

  /// 下载文件
  Future<Response> download(
    String path,
    String savePath, {
    Map<String, dynamic>? params,
    Map<String, String>? headers,
    ProgressCallback? onProgress,
  });

  /// 取消���求
  void cancelRequest([String? tag]);

  /// 添加拦截器
  void addInterceptor(Interceptor interceptor);

  /// 移除拦截器
  void removeInterceptor(Interceptor interceptor);
}

/// 网络响应
class Response {
  final dynamic data;
  final int? statusCode;
  final String? statusMessage;
  final Map<String, dynamic> headers;
  final bool isRedirect;
  final String? redirectUrl;

  Response({
    this.data,
    this.statusCode,
    this.statusMessage,
    this.headers = const {},
    this.isRedirect = false,
    this.redirectUrl,
  });

  bool get isSuccess => statusCode != null && statusCode! >= 200 && statusCode! < 300;
}

/// 进度回调
typedef ProgressCallback = void Function(int count, int total);

/// 拦截器接口
abstract class Interceptor {
  /// 请求拦截
  Future<RequestOptions> onRequest(RequestOptions options);

  /// 响应拦截
  Future<Response> onResponse(Response response);

  /// 错误拦截
  Future<dynamic> onError(NetworkException error);
}

/// 请求配置
class RequestOptions {
  final String path;
  final String method;
  final dynamic data;
  final Map<String, dynamic>? params;
  final Map<String, String>? headers;
  final Duration? timeout;
  final String? tag;

  RequestOptions({
    required this.path,
    required this.method,
    this.data,
    this.params,
    this.headers,
    this.timeout,
    this.tag,
  });

  RequestOptions copyWith({
    String? path,
    String? method,
    dynamic data,
    Map<String, dynamic>? params,
    Map<String, String>? headers,
    Duration? timeout,
    String? tag,
  }) {
    return RequestOptions(
      path: path ?? this.path,
      method: method ?? this.method,
      data: data ?? this.data,
      params: params ?? this.params,
      headers: headers ?? this.headers,
      timeout: timeout ?? this.timeout,
      tag: tag ?? this.tag,
    );
  }
}

/// 网络异常
class NetworkException implements Exception {
  final String message;
  final int? code;
  final dynamic data;

  NetworkException({
    required this.message,
    this.code,
    this.data,
  });

  @override
  String toString() => 'NetworkException: $message (code: $code)';
}

/// 多部分文件
class MultipartFile {
  final String filename;
  final Stream<List<int>> stream;
  final int length;
  final String? contentType;

  MultipartFile({
    required this.filename,
    required this.stream,
    required this.length,
    this.contentType,
  });

  /// 从文件创建
  static Future<MultipartFile> fromFile(
    String filePath, {
    String? filename,
    String? contentType,
  }) async {
    final file = File(filePath);
    final length = await file.length();
    final stream = file.openRead();
    return MultipartFile(
      filename: filename ?? basename(filePath),
      stream: stream,
      length: length,
      contentType: contentType,
    );
  }
} 