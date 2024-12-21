import '../data/remote/mysql/knowledge_database.dart';

class RuleTemplateService {
  final KnowledgeDatabase _knowledgeDb;

  RuleTemplateService(this._knowledgeDb);

  // 获取规则模板
  Future<List<RuleTemplate>> getTemplates(RuleType type) async {
    final results = await _knowledgeDb._conn.query('''
      SELECT * FROM rule_templates 
      WHERE rule_type = ? AND is_active = true
      ORDER BY priority DESC
    ''', [type.toString()]);

    return results.map((r) => RuleTemplate.fromJson(r.fields)).toList();
  }

  // 创建规则模板
  Future<String> createTemplate(RuleTemplate template) async {
    final templateId = DateTime.now().millisecondsSinceEpoch.toString();
    
    await _knowledgeDb._conn.query('''
      INSERT INTO rule_templates (
        id, rule_type, name, description, condition_template,
        action_template, params_schema, priority, is_active,
        created_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NOW())
    ''', [
      templateId,
      template.type.toString(),
      template.name,
      template.description,
      jsonEncode(template.conditionTemplate),
      jsonEncode(template.actionTemplate),
      jsonEncode(template.paramsSchema),
      template.priority,
      true,
    ]);

    return templateId;
  }

  // 从模板创建规则
  Future<String> createRuleFromTemplate(
    String templateId,
    Map<String, dynamic> params,
  ) async {
    // 1. 获取模板
    final template = await _getTemplate(templateId);
    if (template == null) {
      throw Exception('模板不存在');
    }

    // 2. 验证参数
    _validateParams(template.paramsSchema, params);

    // 3. 处理模板
    final condition = _processTemplate(template.conditionTemplate, params);
    final actions = _processTemplate(template.actionTemplate, params);

    // 4. 创建规则
    final ruleId = DateTime.now().millisecondsSinceEpoch.toString();
    await _knowledgeDb._conn.query('''
      INSERT INTO business_rules (
        id, rule_type, template_id, condition, actions,
        priority, is_active, created_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, NOW())
    ''', [
      ruleId,
      template.type.toString(),
      templateId,
      jsonEncode(condition),
      jsonEncode(actions),
      template.priority,
      true,
    ]);

    return ruleId;
  }

  // 获取单个模板
  Future<RuleTemplate?> _getTemplate(String templateId) async {
    final results = await _knowledgeDb._conn.query('''
      SELECT * FROM rule_templates WHERE id = ?
    ''', [templateId]);

    if (results.isEmpty) return null;
    return RuleTemplate.fromJson(results.first.fields);
  }

  // 验证参数
  void _validateParams(Map<String, dynamic> schema, Map<String, dynamic> params) {
    for (final field in schema.entries) {
      final value = params[field.key];
      if (value == null && field.value['required'] == true) {
        throw Exception('缺少必需参数: ${field.key}');
      }
      // TODO: 实现更多参数验证
    }
  }

  // 处理模板
  dynamic _processTemplate(dynamic template, Map<String, dynamic> params) {
    if (template is String) {
      return _replaceParams(template, params);
    }
    if (template is Map) {
      return template.map((key, value) =>
        MapEntry(key, _processTemplate(value, params)));
    }
    if (template is List) {
      return template.map((item) => _processTemplate(item, params)).toList();
    }
    return template;
  }

  // 替换参数
  String _replaceParams(String template, Map<String, dynamic> params) {
    return template.replaceAllMapped(
      RegExp(r'\{\{(.*?)\}\}'),
      (match) => params[match.group(1)]?.toString() ?? match.group(0),
    );
  }
}

class RuleTemplate {
  final String id;
  final RuleType type;
  final String name;
  final String description;
  final Map<String, dynamic> conditionTemplate;
  final List<Map<String, dynamic>> actionTemplate;
  final Map<String, dynamic> paramsSchema;
  final int priority;

  RuleTemplate({
    required this.id,
    required this.type,
    required this.name,
    required this.description,
    required this.conditionTemplate,
    required this.actionTemplate,
    required this.paramsSchema,
    required this.priority,
  });

  factory RuleTemplate.fromJson(Map<String, dynamic> json) {
    return RuleTemplate(
      id: json['id'],
      type: RuleType.values.byName(json['rule_type']),
      name: json['name'],
      description: json['description'],
      conditionTemplate: jsonDecode(json['condition_template']),
      actionTemplate: jsonDecode(json['action_template']),
      paramsSchema: jsonDecode(json['params_schema']),
      priority: json['priority'],
    );
  }
} 