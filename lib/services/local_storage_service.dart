class LocalStorageService extends GetxService {
  late Box<HealthRecord> _healthBox;
  late Box<LifeRecord> _lifeBox;
  
  @override
  Future<void> onInit() async {
    super.onInit();
    await _initBoxes();
  }

  Future<void> _initBoxes() async {
    _healthBox = await Hive.openBox<HealthRecord>('health_records');
    _lifeBox = await Hive.openBox<LifeRecord>('life_records');
  }

  // 保存健康记录
  Future<void> saveHealthRecord(HealthRecord record) async {
    await _healthBox.add(record);
  }

  // 获取健康记录
  Future<List<HealthRecord>> getHealthRecords() async {
    return _healthBox.values.toList();
  }

  // 数据备份
  Future<void> backupData() async {
    // 实现本地数据备份功能
  }
} 