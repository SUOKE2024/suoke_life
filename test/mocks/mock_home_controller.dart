import 'package:flutter/foundation.dart';
import 'package:mockito/mockito.dart';
import 'package:suoke_life/app/presentation/controllers/home/home_controller.dart';

class MockHomeController extends Mock implements HomeController {
  final _currentIndex = ValueNotifier<int>(0);

  @override
  ValueNotifier<int> get currentIndex => _currentIndex;

  @override
  void changePage(int index) {
    _currentIndex.value = index;
  }

  @override
  void dispose() {
    _currentIndex.dispose();
  }
}
