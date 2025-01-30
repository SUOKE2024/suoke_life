import '../models/tag.dart';
import '../providers/database_provider.dart';

class TagRepository {
  final DatabaseProvider _db;

  TagRepository(this._db);

  Future<List<Tag>> getAllTags() async {
    final tags = await _db.query(
      'tags',
      orderBy: 'created_at DESC',
    );
    return tags.map((json) => Tag.fromJson(json)).toList();
  }

  Future<void> saveTag(Tag tag) async {
    await _db.insert('tags', tag.toJson());
  }

  Future<void> deleteTag(String id) async {
    await _db.delete(
      'tags',
      where: 'id = ?',
      whereArgs: [id],
    );
  }

  Future<void> updateTag(Tag tag) async {
    await _db.update(
      'tags',
      tag.toJson(),
      where: 'id = ?',
      whereArgs: [tag.id],
    );
  }
} 