class TenantManager {
  static final instance = TenantManager._();
  TenantManager._();

  final _storage = Get.find<StorageManager>();
  final _eventBus = Get.find<EventBus>();
  
  final _tenants = <String, Tenant>{};
  final _currentTenant = Rxn<Tenant>();
  
  bool _isInitialized = false;

  Future<void> initialize() async {
    if (_isInitialized) return;

    // 加载租户配置
    await _loadTenants();
    
    // 恢复当前租户
    await _restoreCurrentTenant();
    
    _isInitialized = true;
  }

  Future<void> _loadTenants() async {
    final tenants = await _storage.getObject<Map<String, dynamic>>(
      'tenants',
      (json) => json,
    );

    if (tenants != null) {
      for (final entry in tenants.entries) {
        _tenants[entry.key] = Tenant.fromJson(entry.value);
      }
    }
  }

  Future<void> _restoreCurrentTenant() async {
    final currentId = await _storage.getString('current_tenant');
    if (currentId != null) {
      _currentTenant.value = _tenants[currentId];
    }
  }

  Future<void> createTenant(Tenant tenant) async {
    if (_tenants.containsKey(tenant.id)) {
      throw TenantException('Tenant already exists: ${tenant.id}');
    }

    _tenants[tenant.id] = tenant;
    await _saveTenants();
    _eventBus.fire(TenantCreatedEvent(tenant));
  }

  Future<void> updateTenant(Tenant tenant) async {
    if (!_tenants.containsKey(tenant.id)) {
      throw TenantException('Tenant not found: ${tenant.id}');
    }

    _tenants[tenant.id] = tenant;
    await _saveTenants();
    _eventBus.fire(TenantUpdatedEvent(tenant));
  }

  Future<void> deleteTenant(String id) async {
    final tenant = _tenants.remove(id);
    if (tenant != null) {
      await _saveTenants();
      _eventBus.fire(TenantDeletedEvent(tenant));
    }
  }

  Future<void> switchTenant(String id) async {
    final tenant = _tenants[id];
    if (tenant == null) {
      throw TenantException('Tenant not found: $id');
    }

    _currentTenant.value = tenant;
    await _storage.setString('current_tenant', id);
    _eventBus.fire(TenantSwitchedEvent(tenant));
  }

  Future<void> _saveTenants() async {
    final tenants = <String, dynamic>{};
    for (final entry in _tenants.entries) {
      tenants[entry.key] = entry.value.toJson();
    }
    await _storage.setObject('tenants', tenants);
  }

  Tenant? getTenant(String id) => _tenants[id];
  List<Tenant> getAllTenants() => List.unmodifiable(_tenants.values);
  Tenant? get currentTenant => _currentTenant.value;
  Stream<Tenant?> get currentTenantStream => _currentTenant.stream;
}

class Tenant {
  final String id;
  final String name;
  final TenantConfig config;
  final Map<String, dynamic> settings;
  final DateTime createdAt;
  bool enabled;

  Tenant({
    required this.id,
    required this.name,
    required this.config,
    this.settings = const {},
    required this.createdAt,
    this.enabled = true,
  });

  Map<String, dynamic> toJson() => {
    'id': id,
    'name': name,
    'config': config.toJson(),
    'settings': settings,
    'createdAt': createdAt.toIso8601String(),
    'enabled': enabled,
  };

  factory Tenant.fromJson(Map<String, dynamic> json) => Tenant(
    id: json['id'],
    name: json['name'],
    config: TenantConfig.fromJson(json['config']),
    settings: Map<String, dynamic>.from(json['settings']),
    createdAt: DateTime.parse(json['createdAt']),
    enabled: json['enabled'],
  );
}

class TenantConfig {
  final String databaseUrl;
  final String apiEndpoint;
  final Map<String, dynamic> features;

  TenantConfig({
    required this.databaseUrl,
    required this.apiEndpoint,
    this.features = const {},
  });

  Map<String, dynamic> toJson() => {
    'databaseUrl': databaseUrl,
    'apiEndpoint': apiEndpoint,
    'features': features,
  };

  factory TenantConfig.fromJson(Map<String, dynamic> json) => TenantConfig(
    databaseUrl: json['databaseUrl'],
    apiEndpoint: json['apiEndpoint'],
    features: Map<String, dynamic>.from(json['features']),
  );
}

class TenantException implements Exception {
  final String message;
  TenantException(this.message);
}

// 租户相关事件
class TenantEvent extends AppEvent {
  final Tenant tenant;
  TenantEvent(this.tenant);
}

class TenantCreatedEvent extends TenantEvent {
  TenantCreatedEvent(super.tenant);
}

class TenantUpdatedEvent extends TenantEvent {
  TenantUpdatedEvent(super.tenant);
}

class TenantDeletedEvent extends TenantEvent {
  TenantDeletedEvent(super.tenant);
}

class TenantSwitchedEvent extends TenantEvent {
  TenantSwitchedEvent(super.tenant);
} 