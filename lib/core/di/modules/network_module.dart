import 'package:dio/dio.dart';
import 'package:injectable/injectable.dart';
import 'package:retrofit/error_logger.dart';

@module
abstract class NetworkModule {
  @singleton
  Dio get dio => Dio(BaseOptions(
        connectTimeout: const Duration(seconds: 30),
        receiveTimeout: const Duration(seconds: 30),
        sendTimeout: const Duration(seconds: 30),
      ));

  @Named('errorLogger')
  @singleton
  ParseErrorLogger get errorLogger => DefaultParseErrorLogger();
} 