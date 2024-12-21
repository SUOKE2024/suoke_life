import 'package:get/get.dart';

class GamesController extends GetxController {
  final _title = 'Games'.obs;
  get title => _title.value;
  
  @override
  void onInit() {
    super.onInit();
    // 初始化游戏列表
  }
  
  @override
  void onReady() {
    super.onReady();
    // 加载游戏数据
  }
  
  @override
  void onClose() {
    super.onClose();
    // 清理资源
  }
} 