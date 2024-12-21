import '../data/remote/mysql/knowledge_database.dart';
import '../data/remote/oss/oss_storage.dart';

enum ContentType {
  article,   // 文章
  video,     // 视频
  audio,     // 音频
  image,     // 图片
  document,  // 文档
}

enum ContentStatus {
  draft,     // 草稿
  reviewing, // 审核中
  published, // 已发布
  rejected,  // 已拒绝
  archived,  // 已归档
}

class ContentService {
  final KnowledgeDatabase _knowledgeDb;
  final OssStorage _ossStorage;

  ContentService(this._knowledgeDb, this._ossStorage);

  // 创建内容
  Future<String> createContent(Content content) async {
    final contentId = DateTime.now().millisecondsSinceEpoch.toString();
    
    // 1. 上传媒体文件
    final mediaUrls = await _uploadMediaFiles(content.mediaFiles);
    
    // 2. 保存内容记录
    await _knowledgeDb._conn.query('''
      INSERT INTO contents (
        id, title, type, status, summary, body, author_id,
        category_id, tags, media_urls, created_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NOW())
    ''', [
      contentId,
      content.title,
      content.type.toString(),
      content.status.toString(),
      content.summary,
      content.body,
      content.authorId,
      content.categoryId,
      content.tags.join(','),
      jsonEncode(mediaUrls),
    ]);

    return contentId;
  }

  // 更新内容
  Future<void> updateContent(String contentId, Map<String, dynamic> updates) async {
    // 处理媒体文件更新
    if (updates['mediaFiles'] != null) {
      final mediaUrls = await _uploadMediaFiles(updates['mediaFiles']);
      updates['media_urls'] = jsonEncode(mediaUrls);
      updates.remove('mediaFiles');
    }

    final setClause = updates.keys.map((key) => '$key = ?').join(', ');
    
    await _knowledgeDb._conn.query('''
      UPDATE contents 
      SET $setClause, updated_at = NOW()
      WHERE id = ?
    ''', [...updates.values, contentId]);
  }

  // 获取内容列表
  Future<List<Content>> getContents({
    String? type,
    String? status,
    String? categoryId,
    String? authorId,
    String? tag,
    int? limit,
    int? offset,
  }) async {
    var query = 'SELECT * FROM contents WHERE 1=1';
    final params = <String>[];
    
    if (type != null) {
      query += ' AND type = ?';
      params.add(type);
    }
    
    if (status != null) {
      query += ' AND status = ?';
      params.add(status);
    }
    
    if (categoryId != null) {
      query += ' AND category_id = ?';
      params.add(categoryId);
    }
    
    if (authorId != null) {
      query += ' AND author_id = ?';
      params.add(authorId);
    }
    
    if (tag != null) {
      query += ' AND tags LIKE ?';
      params.add('%$tag%');
    }
    
    query += ' ORDER BY created_at DESC';
    
    if (limit != null) {
      query += ' LIMIT ?';
      params.add(limit.toString());
      
      if (offset != null) {
        query += ' OFFSET ?';
        params.add(offset.toString());
      }
    }
    
    final results = await _knowledgeDb._conn.query(query, params);
    return results.map((r) => Content.fromJson(r.fields)).toList();
  }

  // 上传媒体文件
  Future<List<String>> _uploadMediaFiles(List<MediaFile> files) async {
    final urls = <String>[];
    
    for (final file in files) {
      final url = await _ossStorage.uploadMedia(
        file.path,
        file.type,
      );
      urls.add(url);
    }
    
    return urls;
  }
}

class Content {
  final String id;
  final String title;
  final ContentType type;
  final ContentStatus status;
  final String summary;
  final String body;
  final String authorId;
  final String categoryId;
  final List<String> tags;
  final List<MediaFile> mediaFiles;

  Content({
    required this.id,
    required this.title,
    required this.type,
    required this.status,
    required this.summary,
    required this.body,
    required this.authorId,
    required this.categoryId,
    required this.tags,
    required this.mediaFiles,
  });

  factory Content.fromJson(Map<String, dynamic> json) {
    return Content(
      id: json['id'],
      title: json['title'],
      type: ContentType.values.byName(json['type']),
      status: ContentStatus.values.byName(json['status']),
      summary: json['summary'],
      body: json['body'],
      authorId: json['author_id'],
      categoryId: json['category_id'],
      tags: (json['tags'] as String).split(','),
      mediaFiles: (jsonDecode(json['media_urls']) as List)
          .map((url) => MediaFile.fromUrl(url))
          .toList(),
    );
  }
}

class MediaFile {
  final String path;
  final String type;

  MediaFile({required this.path, required this.type});

  factory MediaFile.fromUrl(String url) {
    final type = url.split('.').last;
    return MediaFile(path: url, type: type);
  }
} 