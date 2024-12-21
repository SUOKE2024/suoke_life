import 'package:get/get.dart';
import 'package:hive/hive.dart';
import 'package:suoke_life/data/models/tag.dart';

class TagService extends GetxService {
  late Box<Tag> _tagBox;
  
  // 预设标签
  final _defaultTags = [
    '咖啡', '美食', '运动', '阅读', '旅行',
    '学习', '工作', '生活', '兴趣', '探店',
    '健康', '心情', '音乐', '电影', '摄影',
  ];

  @override
  Future<void> onInit() async {
    super.onInit();
    await _initHive();
    await _initDefaultTags();
  }

  Future<void> _initHive() async {
    _tagBox = await Hive.openBox<Tag>('tags');
  }

  Future<void> _initDefaultTags() async {
    if (_tagBox.isEmpty) {
      for (var name in _defaultTags) {
        await addTag(name);
      }
    }
  }

  // 获取所有标签
  List<String> getAllTags() {
    return _tagBox.values.map((tag) => tag.name).toList();
  }

  // 添加标签
  Future<void> addTag(String name) async {
    final tag = Tag(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      name: name,
      createdAt: DateTime.now(),
    );
    await _tagBox.put(tag.id, tag);
  }

  // 删除标签
  Future<void> deleteTag(String id) async {
    await _tagBox.delete(id);
  }

  // 更新标签
  Future<void> updateTag(Tag tag) async {
    await _tagBox.put(tag.id, tag);
  }

  // 获取标签使用次数
  Future<Map<String, int>> getTagUsage() async {
    final usage = <String, int>{};
    // TODO: 实现标签使用统计
    return usage;
  }
} 