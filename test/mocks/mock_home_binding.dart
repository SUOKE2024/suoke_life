import 'package:get/get.dart';
import 'package:suoke_app/app/core/services/storage/storage_service.dart';
import 'package:suoke_app/app/core/services/network/network_service.dart';
import 'package:suoke_app/app/presentation/controllers/home/home_controller.dart';
import 'package:suoke_app/app/presentation/controllers/suoke/suoke_controller.dart';
import 'package:suoke_app/app/presentation/controllers/explore/explore_controller.dart';
import 'package:suoke_app/app/presentation/controllers/life/life_controller.dart';
import 'package:suoke_app/app/services/features/ai/assistants/xiaoi_service.dart';
import 'package:suoke_app/app/services/features/suoke/suoke_service.dart';

class MockHomeBinding extends Bindings {
  final StorageService storageService;
  final NetworkService networkService;
  final XiaoiService xiaoiService;
  final SuokeService suokeService;
  final HomeController homeController;
  final SuokeController suokeController;
  final ExploreController exploreController;
  final LifeController lifeController;

  MockHomeBinding({
    required this.storageService,
    required this.networkService,
    required this.xiaoiService,
    required this.suokeService,
    required this.homeController,
    required this.suokeController,
    required this.exploreController,
    required this.lifeController,
  });

  @override
  void dependencies() {
    Get.lazyPut<StorageService>(() => storageService, fenix: true);
    Get.lazyPut<NetworkService>(() => networkService, fenix: true);
    Get.lazyPut<XiaoiService>(() => xiaoiService, fenix: true);
    Get.lazyPut<SuokeService>(() => suokeService, fenix: true);

    Get.lazyPut<HomeController>(() => homeController, fenix: true);
    Get.lazyPut<SuokeController>(() => suokeController, fenix: true);
    Get.lazyPut<ExploreController>(() => exploreController, fenix: true);
    Get.lazyPut<LifeController>(() => lifeController, fenix: true);
  }
} 