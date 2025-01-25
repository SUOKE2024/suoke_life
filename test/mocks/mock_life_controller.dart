import 'package:get/get.dart';
import 'package:mockito/mockito.dart';
import '../../lib/app/presentation/controllers/life/life_controller.dart';
import '../../lib/app/data/models/life_record.dart';

class MockLifeController  with Mock implements LifeController {
  final _records = <LifeRecord>[].obs;
  final _isLoading = false.obs;

  @override
  RxList<LifeRecord> get records => _records;

  @override
  RxBool get isLoading => _isLoading;

  @override
  void showRecordDetail(LifeRecord record) {}
} 