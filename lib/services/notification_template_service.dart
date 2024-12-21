import '../data/remote/mysql/knowledge_database.dart';

enum TemplateType {
  text,      // 纯文本模板
  rich,      // 富文本模板
  image,     // 图文模板
  action,    // 动作模板
}

class NotificationTemplateService {
  final KnowledgeDatabase _knowledgeDb;

  NotificationTemplateService(this._knowledgeDb);

  // 创建模板
  Future<String> createTemplate(NotificationTemplate template) async {
    final templateId = DateTime.now().millisecondsSinceEpoch.toString();
    
    await _knowledgeDb._conn.query('''
      INSERT INTO notification_templates (
        id, name, type, title_template, content_template,
        variables, metadata, created_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, NOW())
    ''', [
      templateId,
      template.name,
      template.type.toString(),
      template.titleTemplate,
      template.contentTemplate,
      jsonEncode(template.variables),
      template.metadata != null ? jsonEncode(template.metadata) : null,
    ]);

    return templateId;
  }

  // 渲染模板
  Future<RenderedTemplate> renderTemplate(
    String templateId,
    Map<String, dynamic> data,
  ) async {
    final results = await _knowledgeDb._conn.query('''
      SELECT * FROM notification_templates WHERE id = ?
    ''', [templateId]);

    if (results.isEmpty) {
      throw Exception('Template not found: $templateId');
    }

    final template = NotificationTemplate.fromJson(results.first.fields);
    return template.render(data);
  }

  // 获取模板列表
  Future<List<NotificationTemplate>> getTemplates({
    TemplateType? type,
    String? keyword,
  }) async {
    var query = 'SELECT * FROM notification_templates WHERE 1=1';
    final params = <String>[];

    if (type != null) {
      query += ' AND type = ?';
      params.add(type.toString());
    }

    if (keyword != null) {
      query += ' AND (name LIKE ? OR title_template LIKE ? OR content_template LIKE ?)';
      params.addAll(['%$keyword%', '%$keyword%', '%$keyword%']);
    }

    query += ' ORDER BY created_at DESC';

    final results = await _knowledgeDb._conn.query(query, params);
    return results.map((r) => NotificationTemplate.fromJson(r.fields)).toList();
  }

  // 更新模板
  Future<void> updateTemplate(
    String templateId,
    Map<String, dynamic> updates,
  ) async {
    final setClause = updates.keys.map((key) => '$key = ?').join(', ');
    
    await _knowledgeDb._conn.query('''
      UPDATE notification_templates 
      SET $setClause, updated_at = NOW()
      WHERE id = ?
    ''', [...updates.values, templateId]);
  }

  // 删除模板
  Future<void> deleteTemplate(String templateId) async {
    await _knowledgeDb._conn.query('''
      DELETE FROM notification_templates WHERE id = ?
    ''', [templateId]);
  }
}

class NotificationTemplate {
  final String id;
  final String name;
  final TemplateType type;
  final String titleTemplate;
  final String contentTemplate;
  final Map<String, String> variables;
  final Map<String, dynamic>? metadata;
  final DateTime createdAt;
  final DateTime? updatedAt;

  NotificationTemplate({
    required this.id,
    required this.name,
    required this.type,
    required this.titleTemplate,
    required this.contentTemplate,
    required this.variables,
    this.metadata,
    required this.createdAt,
    this.updatedAt,
  });

  factory NotificationTemplate.fromJson(Map<String, dynamic> json) {
    return NotificationTemplate(
      id: json['id'],
      name: json['name'],
      type: TemplateType.values.byName(json['type']),
      titleTemplate: json['title_template'],
      contentTemplate: json['content_template'],
      variables: Map<String, String>.from(jsonDecode(json['variables'])),
      metadata: json['metadata'] != null ? jsonDecode(json['metadata']) : null,
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: json['updated_at'] != null 
          ? DateTime.parse(json['updated_at'])
          : null,
    );
  }

  // 渲染模板
  RenderedTemplate render(Map<String, dynamic> data) {
    var title = titleTemplate;
    var content = contentTemplate;

    // 替换变量
    for (final entry in data.entries) {
      final placeholder = '{{${entry.key}}}';
      title = title.replaceAll(placeholder, entry.value.toString());
      content = content.replaceAll(placeholder, entry.value.toString());
    }

    return RenderedTemplate(
      title: title,
      content: content,
      type: type,
      metadata: metadata,
    );
  }
}

class RenderedTemplate {
  final String title;
  final String content;
  final TemplateType type;
  final Map<String, dynamic>? metadata;

  RenderedTemplate({
    required this.title,
    required this.content,
    required this.type,
    this.metadata,
  });
} 