import 'package:get/get.dart';
import 'package:suoke_life/services/tag_service.dart';

class TagManagerController extends GetxController {
  final TagService _tagService = Get.find();
  
  // 自定义标签列表
  final _customTags = <String>[].obs;
  List<String> get customTags => _customTags;
  
  // 推荐标签列表
  final _recommendedTags = <String>[].obs;
  List<String> get recommendedTags => _recommendedTags;
  
  // 新标签输入
  final _newTag = ''.obs;
  String get newTag => _newTag.value;
  set newTag(String value) => _newTag.value = value;
  
  @override
  void onInit() {
    super.onInit();
    _loadTags();
  }
  
  // 加载标签
  void _loadTags() {
    _customTags.value = _tagService.getCustomTags();
    _recommendedTags.value = _tagService.getRecommendedTags();
  }
  
  // 添加自定义标签
  Future<void> addTag() async {
    if (newTag.trim().isEmpty) {
      Get.snackbar('提示', '标签不能为空');
      return;
    }
    
    if (_customTags.contains(newTag) || _recommendedTags.contains(newTag)) {
      Get.snackbar('提示', '标签已存在');
      return;
    }
    
    await _tagService.addCustomTag(newTag.trim());
    _loadTags();
    newTag = '';
  }
  
  // 删除自定义标签
  Future<void> removeTag(String tag) async {
    await _tagService.removeCustomTag(tag);
    _loadTags();
  }
  
  // 编辑标签
  Future<void> editTag(String oldTag, String newTagName) async {
    if (newTagName.trim().isEmpty) {
      Get.snackbar('提示', '标签不能为空');
      return;
    }
    
    if (_customTags.contains(newTagName) || _recommendedTags.contains(newTagName)) {
      Get.snackbar('提示', '标签已存在');
      return;
    }
    
    await _tagService.removeCustomTag(oldTag);
    await _tagService.addCustomTag(newTagName.trim());
    _loadTags();
  }
} 