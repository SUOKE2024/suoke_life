class MigrationManager {
  static final instance = MigrationManager._();
  MigrationManager._();

  final _storage = Get.find<StorageManager>();
  final _eventBus = Get.find<EventBus>();
  
  final _migrations = <Migration>[];
  final _migrationHistory = <String>{};
  
  bool _isInitialized = false;

  Future<void> initialize() async {
    if (_isInitialized) return;

    // 注册迁移脚本
    _registerMigrations();
    
    // 加载迁移历史
    await _loadMigrationHistory();
    
    // 执行待处理的迁移
    await _runPendingMigrations();
    
    _isInitialized = true;
  }

  void _registerMigrations() {
    _migrations.addAll([
      DatabaseMigration_1_0_0(),
      DatabaseMigration_1_1_0(),
      SettingsMigration_1_0_0(),
      // 添加更多迁移脚本
    ]);
    
    // 按版本号排序
    _migrations.sort((a, b) => a.version.compareTo(b.version));
  }

  Future<void> _loadMigrationHistory() async {
    final history = await _storage.getStringList('migration_history');
    if (history != null) {
      _migrationHistory.addAll(history);
    }
  }

  Future<void> _runPendingMigrations() async {
    final pendingMigrations = _migrations
        .where((m) => !_migrationHistory.contains(m.id))
        .toList();

    if (pendingMigrations.isEmpty) return;

    for (final migration in pendingMigrations) {
      try {
        await _executeMigration(migration);
      } catch (e) {
        _eventBus.fire(MigrationFailedEvent(migration, e));
        rethrow;
      }
    }
  }

  Future<void> _executeMigration(Migration migration) async {
    _eventBus.fire(MigrationStartedEvent(migration));

    await migration.up();
    _migrationHistory.add(migration.id);
    await _saveMigrationHistory();

    _eventBus.fire(MigrationCompletedEvent(migration));
  }

  Future<void> _saveMigrationHistory() async {
    await _storage.setStringList(
      'migration_history',
      _migrationHistory.toList(),
    );
  }

  Future<void> rollback(String version) async {
    final migrationsToRollback = _migrations
        .where((m) => 
            m.version.compareTo(version) > 0 && 
            _migrationHistory.contains(m.id))
        .toList()
        ..sort((a, b) => b.version.compareTo(a.version));

    for (final migration in migrationsToRollback) {
      try {
        await _rollbackMigration(migration);
      } catch (e) {
        _eventBus.fire(MigrationRollbackFailedEvent(migration, e));
        rethrow;
      }
    }
  }

  Future<void> _rollbackMigration(Migration migration) async {
    _eventBus.fire(MigrationRollbackStartedEvent(migration));

    await migration.down();
    _migrationHistory.remove(migration.id);
    await _saveMigrationHistory();

    _eventBus.fire(MigrationRollbackCompletedEvent(migration));
  }

  List<String> get appliedMigrations => List.unmodifiable(_migrationHistory);
  String get currentVersion => _migrations
      .lastWhere((m) => _migrationHistory.contains(m.id))
      .version;
}

abstract class Migration {
  String get id;
  String get version;
  String get description;

  Future<void> up();
  Future<void> down();
}

// 示例迁移脚本
class DatabaseMigration_1_0_0 extends Migration {
  @override
  String get id => 'database_1_0_0';
  @override
  String get version => '1.0.0';
  @override
  String get description => '初始化数据库结构';

  @override
  Future<void> up() async {
    // 创建表等操作
  }

  @override
  Future<void> down() async {
    // 回滚操作
  }
}

// 迁移相关事件
class MigrationEvent extends AppEvent {
  final Migration migration;
  MigrationEvent(this.migration);
}

class MigrationStartedEvent extends MigrationEvent {
  MigrationStartedEvent(super.migration);
}

class MigrationCompletedEvent extends MigrationEvent {
  MigrationCompletedEvent(super.migration);
}

class MigrationFailedEvent extends MigrationEvent {
  final dynamic error;
  MigrationFailedEvent(super.migration, this.error);
}

class MigrationRollbackStartedEvent extends MigrationEvent {
  MigrationRollbackStartedEvent(super.migration);
}

class MigrationRollbackCompletedEvent extends MigrationEvent {
  MigrationRollbackCompletedEvent(super.migration);
}

class MigrationRollbackFailedEvent extends MigrationEvent {
  final dynamic error;
  MigrationRollbackFailedEvent(super.migration, this.error);
} 