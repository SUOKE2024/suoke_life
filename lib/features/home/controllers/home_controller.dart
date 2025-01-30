import 'package:flutter/foundation.dart';

class HomeController {
  final _currentIndex = ValueNotifier<int>(0);

  ValueNotifier<int> get currentIndex => _currentIndex;

  void changePage(int index) {
    _currentIndex.value = index;
  }

  Future<void> refreshData() async {
    // 模拟数据刷新逻辑
    await Future.delayed(Duration(seconds: 1));
  }

  void dispose() {
    _currentIndex.dispose();
  }
} 