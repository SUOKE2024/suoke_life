class PermissionManagerService extends GetxService {
  final SubscriptionService _subscriptionService;
  final SecurityManagerService _securityManager;
  final EventTrackingService _eventTracking;
  final LogManagerService _logManager;
  
  // 权限配置
  static const Map<SubscriptionPlan, Map<String, dynamic>> _permissionConfig = {
    SubscriptionPlan.basic: {
      'features': {
        'chat': {'read', 'write'},
        'history': {'read'},
        'settings': {'read', 'write'},
      },
      'max_roles': 1,
      'custom_roles': false,
    },
    SubscriptionPlan.pro: {
      'features': {
        'chat': {'read', 'write', 'delete'},
        'history': {'read', 'export'},
        'settings': {'read', 'write', 'delete'},
        'analysis': {'read'},
      },
      'max_roles': 5,
      'custom_roles': true,
    },
    SubscriptionPlan.premium: {
      'features': {
        'chat': {'read', 'write', 'delete', 'admin'},
        'history': {'read', 'write', 'delete', 'export'},
        'settings': {'read', 'write', 'delete', 'admin'},
        'analysis': {'read', 'write', 'export'},
        'system': {'read', 'write', 'admin'},
      },
      'max_roles': -1,  // 无限制
      'custom_roles': true,
    },
  };
  
  // 用户角色
  final Map<String, Set<String>> _userRoles = {};
  
  // 自定义角色权限
  final Map<String, Map<String, Set<String>>> _customRoles = {};
  
  PermissionManagerService({
    required SubscriptionService subscriptionService,
    required SecurityManagerService securityManager,
    required EventTrackingService eventTracking,
    required LogManagerService logManager,
  })  : _subscriptionService = subscriptionService,
        _securityManager = securityManager,
        _eventTracking = eventTracking,
        _logManager = logManager;

  Future<bool> checkPermission(
    String userId,
    String feature,
    String action,
  ) async {
    try {
      // 获取用户角色
      final roles = _userRoles[userId] ?? {'user'};  // 默认用户角色
      
      // 检查每个角色的权限
      for (final role in roles) {
        if (await _checkRolePermission(role, feature, action)) {
          return true;
        }
      }
      
      return false;
    } catch (e) {
      await _logManager.log(
        'Permission check failed',
        userId: userId,
        assistantName: 'system',
        level: LogLevel.error,
        metadata: {
          'feature': feature,
          'action': action,
          'error': e.toString(),
        },
      );
      return false;
    }
  }

  Future<void> assignRole(
    String userId,
    String role, {
    Map<String, Set<String>>? permissions,
  }) async {
    try {
      // 验证角色限制
      if (!_canAssignRole(userId, role)) {
        throw AIException(
          '无法分配角色',
          code: 'ROLE_ASSIGNMENT_NOT_ALLOWED',
        );
      }

      // 如果是自定义角色，保存权限
      if (permissions != null) {
        await _createCustomRole(role, permissions);
      }

      // 分配角色
      _userRoles
        .putIfAbsent(userId, () => {})
        .add(role);
      
      // 记录事件
      await _trackRoleEvent(
        userId,
        role,
        'assigned',
        permissions: permissions,
      );
    } catch (e) {
      await _logManager.log(
        'Role assignment failed',
        userId: userId,
        assistantName: 'system',
        level: LogLevel.error,
        metadata: {
          'role': role,
          'error': e.toString(),
        },
      );
      rethrow;
    }
  }

  Future<void> removeRole(String userId, String role) async {
    try {
      _userRoles[userId]?.remove(role);
      
      await _trackRoleEvent(userId, role, 'removed');
    } catch (e) {
      await _logManager.log(
        'Role removal failed',
        userId: userId,
        assistantName: 'system',
        level: LogLevel.error,
        metadata: {
          'role': role,
          'error': e.toString(),
        },
      );
    }
  }

  Future<Set<String>> getUserRoles(String userId) async {
    return _userRoles[userId] ?? {'user'};
  }

  Future<Map<String, Set<String>>> getRolePermissions(String role) async {
    // 检查是否是自定义角色
    if (_customRoles.containsKey(role)) {
      return _customRoles[role]!;
    }
    
    // 返回预定义角色的权限
    final plan = _subscriptionService.currentPlan;
    return _permissionConfig[plan]!['features'] as Map<String, Set<String>>;
  }

  Future<bool> _checkRolePermission(
    String role,
    String feature,
    String action,
  ) async {
    final permissions = await getRolePermissions(role);
    final featurePermissions = permissions[feature];
    
    if (featurePermissions == null) return false;
    
    return featurePermissions.contains(action) ||
           featurePermissions.contains('admin');
  }

  bool _canAssignRole(String userId, String role) {
    final plan = _subscriptionService.currentPlan;
    final config = _permissionConfig[plan]!;
    
    // 检查是否允许自定义角色
    if (role.startsWith('custom_') && !config['custom_roles']) {
      return false;
    }
    
    // 检查角色数量限制
    final maxRoles = config['max_roles'] as int;
    if (maxRoles != -1) {
      final currentRoles = _userRoles[userId]?.length ?? 0;
      if (currentRoles >= maxRoles) return false;
    }
    
    return true;
  }

  Future<void> _createCustomRole(
    String role,
    Map<String, Set<String>> permissions,
  ) async {
    // 验证权限
    if (!await _validatePermissions(permissions)) {
      throw AIException(
        '无效的权限配置',
        code: 'INVALID_PERMISSIONS',
      );
    }
    
    _customRoles[role] = permissions;
  }

  Future<bool> _validatePermissions(
    Map<String, Set<String>> permissions,
  ) async {
    final plan = _subscriptionService.currentPlan;
    final config = _permissionConfig[plan]!;
    final allowedFeatures = config['features'] as Map<String, Set<String>>;
    
    // 检查每个特性的权限
    for (final feature in permissions.keys) {
      if (!allowedFeatures.containsKey(feature)) {
        return false;
      }
      
      final allowedActions = allowedFeatures[feature]!;
      final requestedActions = permissions[feature]!;
      
      // 检查是否包含不允许的操作
      if (!allowedActions.containsAll(requestedActions)) {
        return false;
      }
    }
    
    return true;
  }

  Future<void> _trackRoleEvent(
    String userId,
    String role,
    String action, {
    Map<String, Set<String>>? permissions,
  }) async {
    await _eventTracking.trackEvent(AIEvent(
      id: 'role_${DateTime.now().millisecondsSinceEpoch}',
      userId: userId,
      assistantName: 'system',
      type: AIEventType.role,
      data: {
        'role': role,
        'action': action,
        'permissions': permissions?.map(
          (k, v) => MapEntry(k, v.toList()),
        ),
      },
    ));
  }
} 