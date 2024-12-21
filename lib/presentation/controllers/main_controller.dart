import 'package:get/get.dart';

class MainController extends GetxController {
  final _currentIndex = 0.obs;
  int get currentIndex => _currentIndex.value;
  set currentIndex(int value) => _currentIndex.value = value;

  void changePage(int index) {
    currentIndex = index;
  }

  @override
  void onInit() {
    super.onInit();
  }

  @override
  void onReady() {
    super.onReady();
  }

  @override
  void onClose() {
    super.onClose();
  }
} 