import 'package:elasticsearch/elasticsearch.dart';
import '../data/remote/mysql/knowledge_database.dart';

class SearchService {
  final ElasticClient _esClient;
  final KnowledgeDatabase _knowledgeDb;

  SearchService(this._esClient, this._knowledgeDb);

  // 搜索内容
  Future<SearchResult> search(
    String keyword,
    {
      List<String>? types,
      Map<String, dynamic>? filters,
      String? sortField,
      bool ascending = true,
      int from = 0,
      int size = 10,
    }
  ) async {
    // 构建查询
    final query = {
      'bool': {
        'must': [
          {
            'multi_match': {
              'query': keyword,
              'fields': ['title^3', 'summary^2', 'body', 'tags'],
              'type': 'best_fields',
              'tie_breaker': 0.3,
            },
          },
        ],
        'filter': [],
      },
    };

    // 添加类型过滤
    if (types != null && types.isNotEmpty) {
      query['bool']['filter'].add({
        'terms': {'type': types},
      });
    }

    // 添加自定义过滤
    if (filters != null) {
      filters.forEach((field, value) {
        query['bool']['filter'].add({
          'term': {field: value},
        });
      });
    }

    // 执行搜索
    final response = await _esClient.search(
      index: 'contents',
      body: {
        'query': query,
        'from': from,
        'size': size,
        if (sortField != null) 'sort': [
          {sortField: ascending ? 'asc' : 'desc'},
        ],
        'highlight': {
          'fields': {
            'title': {},
            'summary': {},
            'body': {},
          },
          'pre_tags': ['<em>'],
          'post_tags': ['</em>'],
        },
      },
    );

    // 处理结果
    return SearchResult.fromJson(response);
  }

  // 索引内容
  Future<void> indexContent(Map<String, dynamic> content) async {
    await _esClient.index(
      index: 'contents',
      id: content['id'],
      body: content,
    );
  }

  // 批量索引
  Future<void> bulkIndex(List<Map<String, dynamic>> contents) async {
    final body = [];
    
    for (final content in contents) {
      body.add({'index': {'_index': 'contents', '_id': content['id']}});
      body.add(content);
    }

    await _esClient.bulk(body: body);
  }

  // 删除索引
  Future<void> deleteIndex(String contentId) async {
    await _esClient.delete(
      index: 'contents',
      id: contentId,
    );
  }

  // 更新索引
  Future<void> updateIndex(
    String contentId,
    Map<String, dynamic> updates,
  ) async {
    await _esClient.update(
      index: 'contents',
      id: contentId,
      body: {'doc': updates},
    );
  }

  // 同步数据库到ES
  Future<void> syncToElasticsearch() async {
    var offset = 0;
    const limit = 100;

    while (true) {
      final contents = await _knowledgeDb._conn.query('''
        SELECT * FROM contents 
        ORDER BY id
        LIMIT ? OFFSET ?
      ''', [limit, offset]);

      if (contents.isEmpty) break;

      await bulkIndex(
        contents.map((r) => r.fields).toList(),
      );

      offset += limit;
    }
  }
}

class SearchResult {
  final int total;
  final List<SearchHit> hits;
  final Map<String, dynamic> aggregations;

  SearchResult({
    required this.total,
    required this.hits,
    required this.aggregations,
  });

  factory SearchResult.fromJson(Map<String, dynamic> json) {
    final hits = json['hits']['hits'] as List;
    return SearchResult(
      total: json['hits']['total']['value'],
      hits: hits.map((h) => SearchHit.fromJson(h)).toList(),
      aggregations: json['aggregations'] ?? {},
    );
  }
}

class SearchHit {
  final String id;
  final double score;
  final Map<String, dynamic> source;
  final Map<String, List<String>> highlights;

  SearchHit({
    required this.id,
    required this.score,
    required this.source,
    required this.highlights,
  });

  factory SearchHit.fromJson(Map<String, dynamic> json) {
    final highlights = <String, List<String>>{};
    if (json['highlight'] != null) {
      json['highlight'].forEach((field, value) {
        highlights[field] = List<String>.from(value);
      });
    }

    return SearchHit(
      id: json['_id'],
      score: json['_score'],
      source: json['_source'],
      highlights: highlights,
    );
  }
} 