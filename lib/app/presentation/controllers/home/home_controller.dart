import 'package:flutter/foundation.dart';
import 'package:injectable/injectable.dart';

@injectable
class HomeController {
  final _currentIndex = ValueNotifier<int>(0);

  ValueNotifier<int> get currentIndex => _currentIndex;

  void changePage(int index) {
    _currentIndex.value = index;
  }

  void dispose() {
    _currentIndex.dispose();
  }
} 