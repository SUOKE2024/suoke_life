import 'package:get/get.dart';
import 'package:suoke_life/presentation/controllers/games_controller.dart';

class GamesBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut<GamesController>(() => GamesController());
  }
} 