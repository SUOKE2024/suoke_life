import 'package:core/network/llm_service_client.dart';
import 'package:core/network/multimodal_service_client.dart';
import 'package:core/network/llm_service_client_impl.dart';
import 'package:core/network/multimodal_service_client_impl.dart';
import 'package:health_service/services/health_advice_service.dart';
import 'package:health_service/services/health_advice_service_impl.dart';
import 'package:injectable/injectable.dart';

@module
abstract class HealthServiceModule {
  @lazySingleton
  HealthAdviceService healthAdviceService(
    LocalStorageService localStorage,
    RedisService redis,
    LunarTermService lunarTermService,
    TCMTherapyService tcmService,
    MentalHealthService mentalHealthService,
    FoodTherapyService foodTherapyService,
    AgriculturalProductService productService,
    LLMServiceClient llmClient,
    MultimodalServiceClient multimodalClient,
  ) =>
      HealthAdviceServiceImpl(
        localStorage,
        redis,
        lunarTermService,
        tcmService,
        mentalHealthService,
        foodTherapyService,
        productService,
        llmClient,
        multimodalClient,
      );

  @lazySingleton
  LLMServiceClient llmServiceClient() => LLMServiceClientImpl();

  @lazySingleton
  MultimodalServiceClient multimodalServiceClient() => MultimodalServiceClientImpl();

  @lazySingleton
  LunarTermService lunarTermService() => LunarTermServiceImpl();

  @lazySingleton
  TCMTherapyService tcmTherapyService() => TCMTherapyServiceImpl();

  @lazySingleton
  MentalHealthService mentalHealthService() => MentalHealthServiceImpl();

  @lazySingleton
  AgriculturalProductService agriculturalProductService() => AgriculturalProductServiceImpl();
}
