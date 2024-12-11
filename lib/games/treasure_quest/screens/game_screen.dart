import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import '../services/ar_service.dart';
import '../models/game_config.dart';
import '../models/player.dart';
import '../widgets/ar_overlay.dart';
import '../widgets/game_hud.dart';
import '../widgets/treasure_radar.dart';

class GameScreen extends StatefulWidget {
  final Player player;

  const GameScreen({
    Key? key,
    required this.player,
  }) : super(key: key);

  @override
  State<GameScreen> createState() => _GameScreenState();
}

class _GameScreenState extends State<GameScreen> with WidgetsBindingObserver {
  late ARService _arService;
  CameraController? _cameraController;
  bool _isCameraInitialized = false;
  bool _isARInitialized = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _initializeServices();
  }

  Future<void> _initializeServices() async {
    // 初始化AR服务
    _arService = ARService();
    _isARInitialized = await _arService.initialize();

    // 初始化相机
    final cameras = await availableCameras();
    if (cameras.isNotEmpty) {
      _cameraController = CameraController(
        cameras.first,
        ResolutionPreset.high,
        enableAudio: false,
      );

      await _cameraController?.initialize();
      if (mounted) {
        setState(() {
          _isCameraInitialized = true;
        });
      }
    }
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _cameraController?.dispose();
    _arService.dispose();
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (_cameraController == null || !_cameraController!.value.isInitialized) {
      return;
    }

    if (state == AppLifecycleState.inactive) {
      _cameraController?.dispose();
    } else if (state == AppLifecycleState.resumed) {
      _initializeServices();
    }
  }

  @override
  Widget build(BuildContext context) {
    if (!_isCameraInitialized || !_isARInitialized) {
      return const Scaffold(
        body: Center(
          child: CircularProgressIndicator(),
        ),
      );
    }

    return Scaffold(
      body: Stack(
        children: [
          // 相机预览
          Positioned.fill(
            child: CameraPreview(_cameraController!),
          ),

          // AR叠加层
          Positioned.fill(
            child: StreamBuilder<Map<String, dynamic>>(
              stream: _arService.arView,
              builder: (context, snapshot) {
                if (!snapshot.hasData) {
                  return const SizedBox.shrink();
                }

                return AROverlay(
                  arData: snapshot.data!,
                  player: widget.player,
                );
              },
            ),
          ),

          // 游戏HUD
          Positioned.fill(
            child: GameHUD(
              player: widget.player,
              arService: _arService,
            ),
          ),

          // 宝藏雷达
          Positioned(
            right: 16,
            bottom: 16,
            child: StreamBuilder<double>(
              stream: _arService.compassStream,
              builder: (context, snapshot) {
                return TreasureRadar(
                  bearing: snapshot.data ?? 0.0,
                  player: widget.player,
                  arService: _arService,
                );
              },
            ),
          ),

          // 返回按钮
          Positioned(
            top: MediaQuery.of(context).padding.top + 16,
            left: 16,
            child: IconButton(
              icon: const Icon(
                Icons.arrow_back,
                color: Colors.white,
                size: 32,
              ),
              onPressed: () => Navigator.of(context).pop(),
            ),
          ),
        ],
      ),
    );
  }
} 