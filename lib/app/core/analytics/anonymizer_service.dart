@singleton
class AnonymizerService {
  // 数据脱敏规则
  final Map<String, Function> _anonymizationRules = {
    'userId': (String id) => sha256.convert(utf8.encode(id)).toString().substring(0, 8),
    'location': (Map<String, dynamic> loc) => {
      'city': loc['city'],
      'province': loc['province'],
      'country': loc['country'],
    },
    'deviceInfo': (Map<String, dynamic> device) => {
      'platform': device['platform'],
      'version': device['version'],
      'screenSize': device['screenSize'],
    },
  };

  // 行为数据匿名化
  Map<String, dynamic> anonymizeBehaviorData(Map<String, dynamic> data) {
    return {
      'sessionId': _anonymizationRules['userId'](data['userId']),
      'timestamp': DateTime.now().toUtc().toIso8601String(),
      'actionType': data['actionType'],
      'context': _sanitizeContext(data['context']),
      'metrics': data['metrics'],
    };
  }

  // 知识数据匿名化
  Map<String, dynamic> anonymizeKnowledgeData(Map<String, dynamic> data) {
    return {
      'topicId': data['topicId'],
      'interactions': _sanitizeInteractions(data['interactions']),
      'queries': _sanitizeQueries(data['queries']),
      'relationships': data['relationships'],
    };
  }

  // 系统数据匿名化
  Map<String, dynamic> anonymizeSystemData(Map<String, dynamic> data) {
    return {
      'deviceType': _anonymizationRules['deviceInfo'](data['deviceInfo']),
      'performance': data['performance'],
      'errors': _sanitizeErrors(data['errors']),
      'timestamp': DateTime.now().toUtc().toIso8601String(),
    };
  }

  Map<String, dynamic> _sanitizeContext(Map<String, dynamic> context) {
    return {
      'screen': context['screen'],
      'feature': context['feature'],
      'duration': context['duration'],
    };
  }

  List<Map<String, dynamic>> _sanitizeInteractions(List<dynamic> interactions) {
    return interactions.map((i) => {
      'type': i['type'],
      'duration': i['duration'],
      'result': i['result'],
    }).toList();
  }

  List<String> _sanitizeQueries(List<String> queries) {
    return queries.map((q) => q.toLowerCase().trim()).toList();
  }

  List<Map<String, dynamic>> _sanitizeErrors(List<dynamic> errors) {
    return errors.map((e) => {
      'type': e['type'],
      'code': e['code'],
      'context': e['context'],
    }).toList();
  }
} 