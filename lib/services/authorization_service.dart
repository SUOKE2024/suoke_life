import '../data/remote/mysql/knowledge_database.dart';

enum PermissionType {
  read,    // 读取权限
  write,   // 写入权限
  execute, // 执行权限
  admin,   // 管理权限
}

class AuthorizationService {
  final KnowledgeDatabase _knowledgeDb;

  AuthorizationService(this._knowledgeDb);

  // 检查权限
  Future<bool> checkPermission(
    String userId,
    String resourceId,
    PermissionType permission,
  ) async {
    // 1. 获取用户角色
    final roles = await _getUserRoles(userId);
    
    // 2. 获取角色权限
    final permissions = await _getRolePermissions(roles);
    
    // 3. 检查资源权限
    return permissions.any((p) =>
      p['resource_id'] == resourceId &&
      p['permission_type'] == permission.toString()
    );
  }

  // 授权
  Future<void> grantPermission(
    String roleId,
    String resourceId,
    PermissionType permission,
  ) async {
    await _knowledgeDb._conn.query('''
      INSERT INTO role_permissions (
        role_id, resource_id, permission_type, created_at
      ) VALUES (?, ?, ?, NOW())
    ''', [
      roleId,
      resourceId,
      permission.toString(),
    ]);
  }

  // 撤销权限
  Future<void> revokePermission(
    String roleId,
    String resourceId,
    PermissionType permission,
  ) async {
    await _knowledgeDb._conn.query('''
      DELETE FROM role_permissions 
      WHERE role_id = ? 
        AND resource_id = ? 
        AND permission_type = ?
    ''', [
      roleId,
      resourceId,
      permission.toString(),
    ]);
  }

  // 获取用户角色
  Future<List<Map<String, dynamic>>> _getUserRoles(String userId) async {
    final results = await _knowledgeDb._conn.query('''
      SELECT r.* FROM roles r
      INNER JOIN user_roles ur ON ur.role_id = r.id
      WHERE ur.user_id = ?
    ''', [userId]);

    return results.map((r) => r.fields).toList();
  }

  // 获取角色权限
  Future<List<Map<String, dynamic>>> _getRolePermissions(
    List<Map<String, dynamic>> roles,
  ) async {
    final roleIds = roles.map((r) => r['id']).toList();
    
    final results = await _knowledgeDb._conn.query('''
      SELECT * FROM role_permissions
      WHERE role_id IN (?)
    ''', [roleIds.join(',')]);

    return results.map((r) => r.fields).toList();
  }
} 