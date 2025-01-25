import 'package:dio/dio.dart';
import 'package:injectable/injectable.dart';
import 'package:retrofit/retrofit.dart';
import '../models/ai_service_response.dart';
import '../../../core/error/parse_error_logger.dart';

part 'ai_service_client.g.dart';

@injectable
@RestApi()
abstract class AIServiceClient {
  @factoryMethod
  factory AIServiceClient(
    @Named('aiDio') Dio dio, {
    @Named('aiBaseUrl') String? baseUrl,
    ParseErrorLogger? errorLogger,
  }) = _AIServiceClient;

  @POST('/chat')
  Future<AIServiceResponse> chat(@Body() Map<String, dynamic> request);
} 