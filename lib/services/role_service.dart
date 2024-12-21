import '../data/remote/mysql/knowledge_database.dart';

class RoleService {
  final KnowledgeDatabase _knowledgeDb;

  RoleService(this._knowledgeDb);

  // 创建角色
  Future<String> createRole(Role role) async {
    final roleId = DateTime.now().millisecondsSinceEpoch.toString();
    
    await _knowledgeDb._conn.query('''
      INSERT INTO roles (
        id, name, description, type, priority, created_at
      ) VALUES (?, ?, ?, ?, ?, NOW())
    ''', [
      roleId,
      role.name,
      role.description,
      role.type.toString(),
      role.priority,
    ]);

    return roleId;
  }

  // 分配角色
  Future<void> assignRole(String userId, String roleId) async {
    await _knowledgeDb._conn.query('''
      INSERT INTO user_roles (
        user_id, role_id, created_at
      ) VALUES (?, ?, NOW())
    ''', [userId, roleId]);
  }

  // 移除角色
  Future<void> removeRole(String userId, String roleId) async {
    await _knowledgeDb._conn.query('''
      DELETE FROM user_roles 
      WHERE user_id = ? AND role_id = ?
    ''', [userId, roleId]);
  }

  // 获取角色列表
  Future<List<Role>> getRoles({String? type}) async {
    var query = 'SELECT * FROM roles';
    final params = <String>[];
    
    if (type != null) {
      query += ' WHERE type = ?';
      params.add(type);
    }
    
    query += ' ORDER BY priority DESC';
    
    final results = await _knowledgeDb._conn.query(query, params);
    return results.map((r) => Role.fromJson(r.fields)).toList();
  }

  // 获取用户角色
  Future<List<Role>> getUserRoles(String userId) async {
    final results = await _knowledgeDb._conn.query('''
      SELECT r.* FROM roles r
      INNER JOIN user_roles ur ON ur.role_id = r.id
      WHERE ur.user_id = ?
      ORDER BY r.priority DESC
    ''', [userId]);

    return results.map((r) => Role.fromJson(r.fields)).toList();
  }

  // 更新角色
  Future<void> updateRole(String roleId, Map<String, dynamic> updates) async {
    final setClause = updates.keys.map((key) => '$key = ?').join(', ');
    
    await _knowledgeDb._conn.query('''
      UPDATE roles 
      SET $setClause, updated_at = NOW()
      WHERE id = ?
    ''', [...updates.values, roleId]);
  }
}

enum RoleType {
  system,    // 系统角色
  business,  // 业务角色
  custom,    // 自定义角色
}

class Role {
  final String id;
  final String name;
  final String description;
  final RoleType type;
  final int priority;

  Role({
    required this.id,
    required this.name,
    required this.description,
    required this.type,
    required this.priority,
  });

  factory Role.fromJson(Map<String, dynamic> json) {
    return Role(
      id: json['id'],
      name: json['name'],
      description: json['description'],
      type: RoleType.values.byName(json['type']),
      priority: json['priority'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'type': type.toString(),
      'priority': priority,
    };
  }
} 