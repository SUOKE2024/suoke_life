import 'package:dio/dio.dart';
import 'package:injectable/injectable.dart';

@injectable
class ParseErrorLogger {
  void logError(Object error, StackTrace stackTrace, RequestOptions options) {
    // TODO: 实现错误日志记录
    print('Error parsing response: $error');
    print('Stack trace: $stackTrace');
    print('Request: ${options.uri}');
  }
} 