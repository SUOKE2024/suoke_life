import 'package:flutter/material.dart';
import 'package:camera/camera.dart';

class VideoPreview extends StatefulWidget {
  const VideoPreview({Key? key}) : super(key: key);

  @override
  _VideoPreviewState createState() => _VideoPreviewState();
}

class _VideoPreviewState extends State<VideoPreview> {
  CameraController? _controller;
  List<CameraDescription> _cameras = [];

  @override
  void initState() {
    super.initState();
    _initializeCamera();
  }

  Future<void> _initializeCamera() async {
    try {
      _cameras = await availableCameras();
      if (_cameras.isEmpty) {
        return;
      }

      _controller = CameraController(
        _cameras.first,
        ResolutionPreset.medium,
        enableAudio: false,
      );

      await _controller!.initialize();
      if (mounted) {
        setState(() {});
      }
    } catch (e) {
      print('Camera initialization error: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_controller == null || !_controller!.value.isInitialized) {
      return const Center(
        child: CircularProgressIndicator(),
      );
    }

    return ClipRRect(
      borderRadius: BorderRadius.circular(12),
      child: AspectRatio(
        aspectRatio: _controller!.value.aspectRatio,
        child: CameraPreview(_controller!),
      ),
    );
  }

  @override
  void dispose() {
    _controller?.dispose();
    super.dispose();
  }
} 