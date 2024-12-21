import 'package:get/get.dart';
import 'package:file_picker/file_picker.dart';
import '../../core/base/base_controller.dart';
import '../../services/group_files_service.dart';
import '../../data/models/group_file.dart';
import 'dart:io';

class GroupFilesController extends BaseController {
  final _filesService = Get.find<GroupFilesService>();
  final String groupId;

  final isLoading = false.obs;
  final files = <GroupFile>[].obs;
  final selectedFileType = 'all'.obs;
  final sortMethod = 'time'.obs;

  // 存储空间
  final usedSpace = 0.obs;
  final remainingSpace = 0.obs;
  final totalSpace = 0.obs;

  double get spaceUsagePercent => usedSpace.value / totalSpace.value;

  GroupFilesController({required this.groupId});

  @override
  void onInit() {
    super.onInit();
    _loadFiles();
    _loadStorageInfo();
    ever(selectedFileType, (_) => _loadFiles());
    ever(sortMethod, (_) => _sortFiles());
  }

  Future<void> _loadFiles() async {
    try {
      isLoading.value = true;
      final result = await _filesService.getFiles(
        groupId,
        type: selectedFileType.value == 'all' ? null : selectedFileType.value,
      );
      files.value = result;
      _sortFiles();
    } catch (e) {
      showError('加载文件失败');
    } finally {
      isLoading.value = false;
    }
  }

  Future<void> _loadStorageInfo() async {
    try {
      final info = await _filesService.getStorageInfo(groupId);
      usedSpace.value = info['used'];
      remainingSpace.value = info['remaining'];
      totalSpace.value = info['total'];
    } catch (e) {
      showError('加载存储信息失败');
    }
  }

  void _sortFiles() {
    switch (sortMethod.value) {
      case 'time':
        files.sort((a, b) => b.uploadTime.compareTo(a.uploadTime));
        break;
      case 'size':
        files.sort((a, b) => b.size.compareTo(a.size));
        break;
      case 'name':
        files.sort((a, b) => a.name.compareTo(b.name));
        break;
      case 'type':
        files.sort((a, b) => a.type.compareTo(b.type));
        break;
    }
  }

  void onSortMethodChanged(String method) {
    sortMethod.value = method;
  }

  Future<void> uploadFile() async {
    try {
      final result = await FilePicker.platform.pickFiles();
      if (result != null) {
        final file = File(result.files.single.path!);
        final fileSize = await file.length();

        // 检查存储空间
        if (fileSize > remainingSpace.value) {
          showError('存储空间不足');
          return;
        }

        showLoading('正在上传...');
        await _filesService.uploadFile(
          groupId,
          file,
          onProgress: (progress) {
            updateLoading('正在上传... ${(progress * 100).toStringAsFixed(1)}%');
          },
        );
        hideLoading();
        showSuccess('上传成功');
        _loadFiles();
        _loadStorageInfo();
      }
    } catch (e) {
      hideLoading();
      showError('上传失败');
    }
  }

  Future<void> downloadFile(GroupFile file) async {
    try {
      showLoading('正在下载...');
      await _filesService.downloadFile(
        file,
        onProgress: (progress) {
          updateLoading('正在下载... ${(progress * 100).toStringAsFixed(1)}%');
        },
      );
      hideLoading();
      showSuccess('下载成功');
    } catch (e) {
      hideLoading();
      showError('下载失败');
    }
  }

  void showDeleteConfirm(GroupFile file) {
    Get.dialog(
      AlertDialog(
        title: const Text('删除文件'),
        content: Text('确定要删除文件"${file.name}"吗？'),
        actions: [
          TextButton(
            onPressed: () => Get.back(),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () {
              Get.back();
              _deleteFile(file);
            },
            style: TextButton.styleFrom(foregroundColor: Colors.red),
            child: const Text('删除'),
          ),
        ],
      ),
    );
  }

  Future<void> _deleteFile(GroupFile file) async {
    try {
      await _filesService.deleteFile(groupId, file.id);
      files.removeWhere((f) => f.id == file.id);
      _loadStorageInfo();
      showSuccess('删除成功');
    } catch (e) {
      showError('删除失败');
    }
  }

  Future<void> openFile(GroupFile file) async {
    try {
      await _filesService.openFile(file);
    } catch (e) {
      showError('打开文件失败');
    }
  }

  String formatFileSize(int bytes) {
    if (bytes < 1024) return '$bytes B';
    if (bytes < 1024 * 1024) return '${(bytes / 1024).toStringAsFixed(1)} KB';
    if (bytes < 1024 * 1024 * 1024) {
      return '${(bytes / (1024 * 1024)).toStringAsFixed(1)} MB';
    }
    return '${(bytes / (1024 * 1024 * 1024)).toStringAsFixed(1)} GB';
  }
} 