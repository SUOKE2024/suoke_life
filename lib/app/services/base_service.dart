import 'package:get/get.dart';

abstract class BaseService extends GetxService {
  Future<void> init();
  Future<void> dispose();
} 