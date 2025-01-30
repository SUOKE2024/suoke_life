class PermissionManager {
  static final instance = PermissionManager._();
  PermissionManager._();

  final _storage = Get.find<StorageManager>();
  final _eventBus = Get.find<EventBus>();
  
  final _permissions = <String, Set<Permission>>{};
  final _rolePermissions = <String, Set<Permission>>{};
  final _userRoles = <String, Set<String>>{};
  
  bool _isInitialized = false;

  Future<void> initialize() async {
    if (_isInitialized) return;

    // 加载权限配置
    await _loadPermissionConfig();
    
    // 加载角色权限
    await _loadRolePermissions();
    
    // 加载用户角色
    await _loadUserRoles();
    
    _isInitialized = true;
  }

  Future<void> _loadPermissionConfig() async {
    final config = await rootBundle.loadString('assets/config/permissions.yaml');
    final yaml = loadYaml(config) as YamlMap;
    
    for (final entry in yaml.entries) {
      final moduleName = entry.key as String;
      final perms = (entry.value as YamlList).map((p) => Permission(p)).toSet();
      _permissions[moduleName] = perms;
    }
  }

  Future<void> _loadRolePermissions() async {
    final rolePerms = await _storage.getObject<Map<String, dynamic>>(
      'role_permissions',
      (json) => json,
    );

    if (rolePerms != null) {
      for (final entry in rolePerms.entries) {
        _rolePermissions[entry.key] = (entry.value as List)
            .map((p) => Permission(p))
            .toSet();
      }
    }
  }

  Future<void> _loadUserRoles() async {
    final userRoles = await _storage.getObject<Map<String, dynamic>>(
      'user_roles',
      (json) => json,
    );

    if (userRoles != null) {
      for (final entry in userRoles.entries) {
        _userRoles[entry.key] = (entry.value as List)
            .map((r) => r as String)
            .toSet();
      }
    }
  }

  Future<void> assignRoleToUser(String userId, String role) async {
    _userRoles.putIfAbsent(userId, () => {}).add(role);
    await _saveUserRoles();
    _eventBus.fire(UserRoleChangedEvent(userId));
  }

  Future<void> removeRoleFromUser(String userId, String role) async {
    _userRoles[userId]?.remove(role);
    await _saveUserRoles();
    _eventBus.fire(UserRoleChangedEvent(userId));
  }

  Future<void> setRolePermissions(String role, Set<Permission> permissions) async {
    _rolePermissions[role] = permissions;
    await _saveRolePermissions();
    _eventBus.fire(RolePermissionsChangedEvent(role));
  }

  bool hasPermission(String userId, Permission permission) {
    final userRoles = _userRoles[userId] ?? {};
    return userRoles.any((role) => 
      _rolePermissions[role]?.contains(permission) ?? false
    );
  }

  bool hasAnyPermission(String userId, List<Permission> permissions) {
    return permissions.any((p) => hasPermission(userId, p));
  }

  bool hasAllPermissions(String userId, List<Permission> permissions) {
    return permissions.every((p) => hasPermission(userId, p));
  }

  Set<Permission> getUserPermissions(String userId) {
    final permissions = <Permission>{};
    final roles = _userRoles[userId] ?? {};
    
    for (final role in roles) {
      permissions.addAll(_rolePermissions[role] ?? {});
    }
    
    return permissions;
  }

  Set<String> getUserRoles(String userId) {
    return Set.from(_userRoles[userId] ?? {});
  }

  Future<void> _saveRolePermissions() async {
    final rolePerms = <String, dynamic>{};
    for (final entry in _rolePermissions.entries) {
      rolePerms[entry.key] = entry.value.map((p) => p.toString()).toList();
    }
    await _storage.setObject('role_permissions', rolePerms);
  }

  Future<void> _saveUserRoles() async {
    final userRoles = <String, dynamic>{};
    for (final entry in _userRoles.entries) {
      userRoles[entry.key] = entry.value.toList();
    }
    await _storage.setObject('user_roles', userRoles);
  }
}

class Permission {
  final String value;
  
  const Permission(this.value);
  
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is Permission &&
          runtimeType == other.runtimeType &&
          value == other.value;

  @override
  int get hashCode => value.hashCode;

  @override
  String toString() => value;
}

// 权限相关事件
class UserRoleChangedEvent extends AppEvent {
  final String userId;
  UserRoleChangedEvent(this.userId);
}

class RolePermissionsChangedEvent extends AppEvent {
  final String role;
  RolePermissionsChangedEvent(this.role);
} 