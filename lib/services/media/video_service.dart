import 'dart:io';
import 'package:image_picker/image_picker.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:video_player/video_player.dart';
import '../storage/storage_quota_service.dart';

class VideoService {
  final ImagePicker _picker;
  final StorageQuotaService _quotaService;
  VideoPlayerController? _controller;

  VideoService(this._quotaService) : _picker = ImagePicker();

  Future<File?> pickVideo({
    ImageSource source = ImageSource.gallery,
    Duration maxDuration = const Duration(minutes: 10),
  }) async {
    final permission = source == ImageSource.camera
        ? Permission.camera
        : Permission.photos;
    
    final status = await permission.request();
    if (status != PermissionStatus.granted) {
      throw Exception('需要${source == ImageSource.camera ? "相机" : "相册"}权限');
    }

    final video = await _picker.pickVideo(
      source: source,
      maxDuration: maxDuration,
    );

    if (video != null) {
      final file = File(video.path);
      final size = await file.length();
      
      if (!await _quotaService.checkStorageAvailable(size)) {
        throw Exception('存储空间不足');
      }

      return file;
    }
    return null;
  }

  Future<void> initializePlayer(String path) async {
    _controller?.dispose();
    
    if (path.startsWith('http')) {
      _controller = VideoPlayerController.network(path);
    } else {
      _controller = VideoPlayerController.file(File(path));
    }

    await _controller!.initialize();
  }

  Future<void> play() async {
    await _controller?.play();
  }

  Future<void> pause() async {
    await _controller?.pause();
  }

  Future<void> seekTo(Duration position) async {
    await _controller?.seekTo(position);
  }

  Future<void> dispose() async {
    await _controller?.dispose();
    _controller = null;
  }

  VideoPlayerController? get controller => _controller;
} 