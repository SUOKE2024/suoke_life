import '../data/remote/mysql/knowledge_database.dart';

enum RuleType {
  payment,    // 支付规则
  risk,       // 风控规则
  promotion,  // 促销规则
  game,       // 游戏规则
}

class RuleEngineService {
  final KnowledgeDatabase _knowledgeDb;

  RuleEngineService(this._knowledgeDb);

  // 执行规则
  Future<RuleResult> executeRules(
    RuleType type,
    Map<String, dynamic> context,
  ) async {
    // 1. 加载规则
    final rules = await _loadRules(type);
    
    // 2. 规则排序
    rules.sort((a, b) => b['priority'].compareTo(a['priority']));

    // 3. 执行规则
    final results = <String, dynamic>{};
    final actions = <String>[];

    for (final rule in rules) {
      if (await _evaluateCondition(rule['condition'], context)) {
        // 规则匹配,执行动作
        final ruleActions = await _executeActions(rule['actions'], context);
        actions.addAll(ruleActions);
        
        // 更新上下文
        context['rule_results'] = results;
        
        // 检查是否需要中断
        if (rule['break_on_match'] == true) break;
      }
    }

    return RuleResult(
      matched: actions.isNotEmpty,
      actions: actions,
      context: context,
    );
  }

  // 加载规则
  Future<List<Map<String, dynamic>>> _loadRules(RuleType type) async {
    final results = await _knowledgeDb._conn.query('''
      SELECT * FROM business_rules 
      WHERE rule_type = ? AND is_active = true
      ORDER BY priority DESC
    ''', [type.toString()]);

    return results.map((r) {
      final raw = r.fields;
      return {
        'id': raw['id'],
        'priority': raw['priority'],
        'condition': jsonDecode(raw['condition']),
        'actions': jsonDecode(raw['actions']),
        'break_on_match': raw['break_on_match'],
      };
    }).toList();
  }

  // 评估条件
  Future<bool> _evaluateCondition(
    Map<String, dynamic> condition,
    Map<String, dynamic> context,
  ) async {
    final operator = condition['operator'];
    final field = condition['field'];
    final value = condition['value'];

    final fieldValue = _getFieldValue(context, field);

    switch (operator) {
      case 'equals':
        return fieldValue == value;
      case 'not_equals':
        return fieldValue != value;
      case 'greater_than':
        return fieldValue > value;
      case 'less_than':
        return fieldValue < value;
      case 'contains':
        return fieldValue.toString().contains(value);
      case 'in':
        return (value as List).contains(fieldValue);
      case 'and':
        for (final subCondition in condition['conditions']) {
          if (!await _evaluateCondition(subCondition, context)) {
            return false;
          }
        }
        return true;
      case 'or':
        for (final subCondition in condition['conditions']) {
          if (await _evaluateCondition(subCondition, context)) {
            return true;
          }
        }
        return false;
      default:
        throw Exception('不支持的操作符: $operator');
    }
  }

  // 执行动作
  Future<List<String>> _executeActions(
    List<Map<String, dynamic>> actions,
    Map<String, dynamic> context,
  ) async {
    final results = <String>[];
    
    for (final action in actions) {
      final type = action['type'];
      final params = action['params'];
      
      switch (type) {
        case 'set_field':
          context[params['field']] = params['value'];
          results.add('设置字段: ${params['field']} = ${params['value']}');
          break;
        case 'apply_discount':
          final amount = context['amount'] * (1 - params['discount']);
          context['final_amount'] = amount;
          results.add('应用折扣: ${params['discount']}');
          break;
        // ... 其他动作类型
        default:
          throw Exception('不支持的动作类型: $type');
      }
    }

    return results;
  }

  dynamic _getFieldValue(Map<String, dynamic> context, String field) {
    final parts = field.split('.');
    dynamic value = context;
    
    for (final part in parts) {
      if (value is! Map) return null;
      value = value[part];
    }
    
    return value;
  }
}

class RuleResult {
  final bool matched;
  final List<String> actions;
  final Map<String, dynamic> context;

  RuleResult({
    required this.matched,
    required this.actions,
    required this.context,
  });
} 