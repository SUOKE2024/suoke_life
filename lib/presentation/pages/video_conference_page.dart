import 'package:flutter/material.dart';
import 'package:get_it/get_it.dart';
import '../widgets/video_preview.dart';
import '../widgets/visualization_chart.dart';
import '../widgets/connection_status_widget.dart';
import '../widgets/error_dialog.dart';
import '../../services/realtime_data_collection_service.dart';
import '../../services/biometric_analysis_service.dart';
import '../../services/realtime_visualization_service.dart';
import '../../services/secure_data_transport_service.dart';
import '../../services/permission_manager_service.dart';
import '../../services/error_handler_service.dart';
import '../../services/connection_manager_service.dart';

class VideoConferencePage extends StatefulWidget {
  const VideoConferencePage({Key? key}) : super(key: key);

  @override
  _VideoConferencePageState createState() => _VideoConferencePageState();
}

class _VideoConferencePageState extends State<VideoConferencePage> {
  late final RealtimeDataCollectionService _dataCollectionService;
  late final BiometricAnalysisService _analysisService;
  late final RealtimeVisualizationService _visualizationService;
  late final SecureDataTransportService _transportService;
  late final PermissionManagerService _permissionService;
  late final ErrorHandlerService _errorHandler;
  late final ConnectionManagerService _connectionManager;
  
  bool _isCollecting = false;
  bool _isAnalyzing = false;
  bool _isVisualizing = false;
  bool _permissionsGranted = false;

  @override
  void initState() {
    super.initState();
    _initializeServices();
    _checkPermissions();
    _setupErrorHandling();
  }

  void _initializeServices() {
    final getIt = GetIt.instance;
    _dataCollectionService = getIt<RealtimeDataCollectionService>();
    _analysisService = getIt<BiometricAnalysisService>();
    _visualizationService = getIt<RealtimeVisualizationService>();
    _transportService = getIt<SecureDataTransportService>();
    _permissionService = getIt<PermissionManagerService>();
    _errorHandler = getIt<ErrorHandlerService>();
    _connectionManager = getIt<ConnectionManagerService>();
  }

  Future<void> _checkPermissions() async {
    try {
      _permissionsGranted = await _permissionService.requestVideoConferencePermissions();
      if (!_permissionsGranted) {
        _showPermissionDialog();
      }
    } catch (e) {
      _errorHandler.handlePermissionError('权限检查失败');
    }
  }

  void _setupErrorHandling() {
    _errorHandler.errorStream.listen((error) {
      _showErrorDialog(error);
    });
  }

  void _showPermissionDialog() {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        title: const Text('需要权限'),
        content: const Text('视频会议需要相机和麦克风权限才能正常运行。'),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              Navigator.pop(context);
            },
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () async {
              Navigator.pop(context);
              await _permissionService.openAppSettings();
            },
            child: const Text('打开设置'),
          ),
        ],
      ),
    );
  }

  void _showErrorDialog(VideoConferenceError error) {
    showDialog(
      context: context,
      builder: (context) => ErrorDialog(error: error),
    );
  }

  Future<void> _startDataCollection() async {
    if (!_permissionsGranted) {
      _showPermissionDialog();
      return;
    }

    try {
      await _connectionManager.connect();
      
      setState(() {
        _isCollecting = true;
        _isAnalyzing = true;
        _isVisualizing = true;
      });

      _dataCollectionService.startCollection();
      _analysisService.startAnalysis();
      _visualizationService.startVisualization();
    } catch (e, stackTrace) {
      _errorHandler.handleError(
        'START_FAILED',
        '启动视频会议失败',
        ErrorSeverity.high,
        originalError: e,
        stackTrace: stackTrace,
      );
    }
  }

  Future<void> _stopDataCollection() async {
    try {
      setState(() {
        _isCollecting = false;
        _isAnalyzing = false;
        _isVisualizing = false;
      });

      _dataCollectionService.stopCollection();
      _analysisService.stopAnalysis();
      _visualizationService.stopVisualization();
      await _connectionManager.disconnect();
    } catch (e, stackTrace) {
      _errorHandler.handleError(
        'STOP_FAILED',
        '停止视频会议失败',
        ErrorSeverity.medium,
        originalError: e,
        stackTrace: stackTrace,
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('视频会议'),
        actions: [
          StreamBuilder<ConnectionState>(
            stream: _connectionManager.connectionState,
            builder: (context, snapshot) {
              return ConnectionStatusWidget(
                state: snapshot.data ?? ConnectionState.disconnected,
              );
            },
          ),
          IconButton(
            icon: Icon(_isCollecting ? Icons.stop : Icons.play_arrow),
            onPressed: _isCollecting ? _stopDataCollection : _startDataCollection,
          ),
        ],
      ),
      body: Column(
        children: [
          // 视频预览区域
          Expanded(
            flex: 2,
            child: Row(
              children: [
                // 本地视频预览
                Expanded(
                  child: VideoPreview(
                    isLocal: true,
                    onFrameAvailable: _dataCollectionService.processVideoFrame,
                    onError: (error) => _errorHandler.handleCameraError(error, StackTrace.current),
                  ),
                ),
                // 远程视频预览
                Expanded(
                  child: VideoPreview(
                    isLocal: false,
                  ),
                ),
              ],
            ),
          ),
          // 数据可视化区域
          if (_isVisualizing)
            Expanded(
              flex: 1,
              child: StreamBuilder<List<VisualizationData>>(
                stream: _visualizationService.visualizationStream,
                builder: (context, snapshot) {
                  if (!snapshot.hasData) {
                    return const Center(child: CircularProgressIndicator());
                  }

                  return ListView.builder(
                    scrollDirection: Axis.horizontal,
                    itemCount: snapshot.data!.length,
                    itemBuilder: (context, index) {
                      final data = snapshot.data![index];
                      return SizedBox(
                        width: 300,
                        child: Card(
                          margin: const EdgeInsets.all(8),
                          child: Padding(
                            padding: const EdgeInsets.all(8),
                            child: Column(
                              children: [
                                Text(
                                  data.title,
                                  style: Theme.of(context).textTheme.subtitle1,
                                ),
                                Expanded(
                                  child: VisualizationChart(
                                    data: data,
                                    chartData: _visualizationService.generateChartData(data),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      );
                    },
                  );
                },
              ),
            ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _stopDataCollection();
    super.dispose();
  }
} 