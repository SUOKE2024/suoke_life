import 'package:flutter/material.dart';
import 'package:video_player/video_player.dart';
import 'package:chewie/chewie.dart';

class VideoPlayerWidget extends StatefulWidget {
  final String url;
  final String? thumbnail;
  final bool autoPlay;
  final bool looping;

  const VideoPlayerWidget({
    Key? key,
    required this.url,
    this.thumbnail,
    this.autoPlay = false,
    this.looping = false,
  }) : super(key: key);

  @override
  State<VideoPlayerWidget> createState() => _VideoPlayerWidgetState();
}

class _VideoPlayerWidgetState extends State<VideoPlayerWidget> {
  late VideoPlayerController _videoPlayerController;
  ChewieController? _chewieController;
  bool _isInitialized = false;

  @override
  void initState() {
    super.initState();
    _initializePlayer();
  }

  Future<void> _initializePlayer() async {
    _videoPlayerController = VideoPlayerController.network(widget.url);
    try {
      await _videoPlayerController.initialize();
      _chewieController = ChewieController(
        videoPlayerController: _videoPlayerController,
        autoPlay: widget.autoPlay,
        looping: widget.looping,
        placeholder: widget.thumbnail != null
            ? Image.network(
                widget.thumbnail!,
                fit: BoxFit.cover,
              )
            : null,
        aspectRatio: _videoPlayerController.value.aspectRatio,
        autoInitialize: true,
        errorBuilder: (context, errorMessage) {
          return Center(
            child: Text(
              errorMessage,
              style: const TextStyle(color: Colors.white),
            ),
          );
        },
      );
      setState(() => _isInitialized = true);
    } catch (e) {
      debugPrint('视频初始化失败: $e');
    }
  }

  @override
  void dispose() {
    _videoPlayerController.dispose();
    _chewieController?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AspectRatio(
      aspectRatio: 16 / 9,
      child: _isInitialized
          ? Chewie(controller: _chewieController!)
          : Stack(
              alignment: Alignment.center,
              children: [
                if (widget.thumbnail != null)
                  Image.network(
                    widget.thumbnail!,
                    fit: BoxFit.cover,
                  ),
                const CircularProgressIndicator(),
              ],
            ),
    );
  }
} 