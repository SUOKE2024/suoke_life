import 'package:get/get.dart';

abstract class BaseFeatureService extends GetxService {
  Future<void> init();
  Future<void> dispose();
} 