import '../data/remote/mysql/knowledge_database.dart';

enum ResourceType {
  menu,      // 菜单
  page,      // 页面
  api,       // 接口
  file,      // 文件
  function,  // 功能
}

class ResourceService {
  final KnowledgeDatabase _knowledgeDb;

  ResourceService(this._knowledgeDb);

  // 创建资源
  Future<String> createResource(Resource resource) async {
    final resourceId = DateTime.now().millisecondsSinceEpoch.toString();
    
    await _knowledgeDb._conn.query('''
      INSERT INTO resources (
        id, name, code, type, parent_id, path, description,
        is_public, created_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, NOW())
    ''', [
      resourceId,
      resource.name,
      resource.code,
      resource.type.toString(),
      resource.parentId,
      resource.path,
      resource.description,
      resource.isPublic ? 1 : 0,
    ]);

    return resourceId;
  }

  // 获取资源树
  Future<List<Resource>> getResourceTree() async {
    final results = await _knowledgeDb._conn.query('''
      SELECT * FROM resources ORDER BY path
    ''');

    final resources = results.map((r) => Resource.fromJson(r.fields)).toList();
    return _buildResourceTree(resources);
  }

  // 获取用户可访问资源
  Future<List<Resource>> getUserResources(String userId) async {
    final results = await _knowledgeDb._conn.query('''
      SELECT DISTINCT r.* FROM resources r
      LEFT JOIN role_permissions rp ON rp.resource_id = r.id
      LEFT JOIN user_roles ur ON ur.role_id = rp.role_id
      WHERE r.is_public = 1 
         OR ur.user_id = ?
      ORDER BY r.path
    ''', [userId]);

    return results.map((r) => Resource.fromJson(r.fields)).toList();
  }

  // 更新资源
  Future<void> updateResource(String resourceId, Map<String, dynamic> updates) async {
    final setClause = updates.keys.map((key) => '$key = ?').join(', ');
    
    await _knowledgeDb._conn.query('''
      UPDATE resources 
      SET $setClause, updated_at = NOW()
      WHERE id = ?
    ''', [...updates.values, resourceId]);
  }

  // 删除资源
  Future<void> deleteResource(String resourceId) async {
    await _knowledgeDb._conn.query('''
      DELETE FROM resources WHERE id = ?
    ''', [resourceId]);

    // 同时删除相关权限
    await _knowledgeDb._conn.query('''
      DELETE FROM role_permissions WHERE resource_id = ?
    ''', [resourceId]);
  }

  // 构建资源树
  List<Resource> _buildResourceTree(List<Resource> resources) {
    final Map<String?, List<Resource>> childrenMap = {};
    
    // 按父ID分组
    for (final resource in resources) {
      childrenMap.putIfAbsent(resource.parentId, () => []).add(resource);
    }
    
    // 递归构建树
    void _setChildren(Resource parent) {
      final children = childrenMap[parent.id];
      if (children != null) {
        parent.children = children;
        for (final child in children) {
          _setChildren(child);
        }
      }
    }
    
    // 获取根节点
    final roots = childrenMap[null] ?? [];
    for (final root in roots) {
      _setChildren(root);
    }
    
    return roots;
  }
}

class Resource {
  final String id;
  final String name;
  final String code;
  final ResourceType type;
  final String? parentId;
  final String path;
  final String description;
  final bool isPublic;
  List<Resource> children;

  Resource({
    required this.id,
    required this.name,
    required this.code,
    required this.type,
    this.parentId,
    required this.path,
    required this.description,
    required this.isPublic,
    this.children = const [],
  });

  factory Resource.fromJson(Map<String, dynamic> json) {
    return Resource(
      id: json['id'],
      name: json['name'],
      code: json['code'],
      type: ResourceType.values.byName(json['type']),
      parentId: json['parent_id'],
      path: json['path'],
      description: json['description'],
      isPublic: json['is_public'] == 1,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'code': code,
      'type': type.toString(),
      'parent_id': parentId,
      'path': path,
      'description': description,
      'is_public': isPublic ? 1 : 0,
      'children': children.map((c) => c.toJson()).toList(),
    };
  }
} 