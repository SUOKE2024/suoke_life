/// 日志拦截器
class LoggingInterceptor implements Interceptor {
  @override
  Future<RequestOptions> onRequest(RequestOptions options) async {
    LoggerService.info('''
    --> ${options.method} ${options.path}
    Headers: ${options.headers}
    Query: ${options.params}
    Body: ${options.data}
    ''');
    return options;
  }

  @override
  Future<Response> onResponse(Response response) async {
    LoggerService.info('''
    <-- ${response.statusCode} ${response.statusMessage}
    Headers: ${response.headers}
    Body: ${response.data}
    ''');
    return response;
  }

  @override
  Future<dynamic> onError(NetworkException error) async {
    LoggerService.error('''
    <-- Error ${error.code}
    Message: ${error.message}
    Data: ${error.data}
    ''');
    return error;
  }
} 