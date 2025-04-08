import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_unity_widget/flutter_unity_widget.dart';
import 'package:auto_route/auto_route.dart';
import 'package:suoke_life/core/constants/app_constants.dart';
import 'package:suoke_life/domain/entities/knowledge_graph.dart';
import 'package:suoke_life/presentation/visualization/providers/visualization_providers.dart';
import 'package:suoke_life/presentation/visualization/widgets/control_panel.dart';
import 'package:suoke_life/presentation/visualization/widgets/loading_overlay.dart';
import 'package:suoke_life/presentation/visualization/widgets/error_overlay.dart';
import 'package:suoke_life/presentation/visualization/performance/index.dart';

@RoutePage()
class KnowledgeGraphViewer extends ConsumerStatefulWidget {
  final String? initialNodeId;
  final VisualizationMode mode;

  const KnowledgeGraphViewer({
    super.key,
    this.initialNodeId,
    this.mode = VisualizationMode.mode3D,
  });

  @override
  ConsumerState<KnowledgeGraphViewer> createState() => _KnowledgeGraphViewerState();
}

class _KnowledgeGraphViewerState extends ConsumerState<KnowledgeGraphViewer> {
  UnityWidgetController? _unityController;
  bool _isLoading = true;
  String? _errorMessage;
  bool _showPerformanceMonitor = false;

  @override
  void initState() {
    super.initState();
    _initializeVisualization();
    // 启动性能监控
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(performanceMonitorProvider.notifier).startMonitoring();
      
      // 启用自动优化
      ref.read(autoOptimizationTriggerProvider.notifier).enable();
    });
  }

  Future<void> _initializeVisualization() async {
    try {
      await ref.read(visualizationControllerProvider.notifier).initialize(
        mode: widget.mode,
        initialNodeId: widget.initialNodeId,
      );
      setState(() => _isLoading = false);
    } catch (e) {
      setState(() {
        _isLoading = false;
        _errorMessage = e.toString();
      });
    }
  }

  void _onUnityCreated(UnityWidgetController controller) {
    setState(() => _unityController = controller);
    ref.read(visualizationControllerProvider.notifier).setUnityController(controller);
    
    // 初始化可视化分析器
    ref.read(visualizationProfilerProvider(controller).notifier).startProfiling();
  }

  void _onUnityMessage(dynamic message) {
    ref.read(visualizationControllerProvider.notifier).handleUnityMessage(message);
  }

  void _togglePerformanceMonitor() {
    setState(() {
      _showPerformanceMonitor = !_showPerformanceMonitor;
    });
  }

  @override
  Widget build(BuildContext context) {
    final visualizationState = ref.watch(visualizationControllerProvider);

    return Scaffold(
      appBar: AppBar(
        title: Text('知识图谱可视化'),
        actions: [
          IconButton(
            icon: Icon(Icons.speed),
            onPressed: _togglePerformanceMonitor,
            tooltip: '性能监控',
          ),
          IconButton(
            icon: Icon(Icons.settings),
            onPressed: () => _showSettingsDialog(context),
          ),
        ],
      ),
      body: Stack(
        children: [
          // Unity视图
          UnityWidget(
            onUnityCreated: _onUnityCreated,
            onUnityMessage: _onUnityMessage,
            fullscreen: false,
          ),
          
          // 控制面板
          Positioned(
            right: 16,
            top: 16,
            child: ControlPanel(
              mode: widget.mode,
              onModeChanged: (mode) {
                ref.read(visualizationControllerProvider.notifier).changeMode(mode);
              },
              onLayoutChanged: (layout) {
                ref.read(visualizationControllerProvider.notifier).changeLayout(layout);
              },
              onFilterChanged: (filter) {
                ref.read(visualizationControllerProvider.notifier).applyFilter(filter);
              },
            ),
          ),

          // 性能监控面板
          if (_showPerformanceMonitor)
            Positioned(
              left: 16,
              top: 16,
              width: 300,
              child: PerformanceMonitorWidget(),
            ),

          // 加载遮罩
          if (_isLoading) LoadingOverlay(),

          // 错误遮罩
          if (_errorMessage != null)
            ErrorOverlay(
              message: _errorMessage!,
              onRetry: () {
                setState(() {
                  _errorMessage = null;
                  _isLoading = true;
                });
                _initializeVisualization();
              },
            ),
        ],
      ),
    );
  }

  Future<void> _showSettingsDialog(BuildContext context) async {
    await showDialog(
      context: context,
      builder: (context) => DefaultTabController(
        length: 3,
        child: AlertDialog(
          title: const Text('可视化设置'),
          content: SizedBox(
            width: 500,
            height: 600,
            child: Column(
              children: [
                TabBar(
                  tabs: const [
                    Tab(icon: Icon(Icons.settings), text: '基础设置'),
                    Tab(icon: Icon(Icons.speed), text: '性能优化'),
                    Tab(icon: Icon(Icons.auto_fix_high), text: '自动优化'),
                  ],
                  labelColor: Theme.of(context).colorScheme.primary,
                  unselectedLabelColor: Colors.grey,
                ),
                Expanded(
                  child: TabBarView(
                    children: [
                      // 基础设置选项卡
                      SingleChildScrollView(
                        child: VisualizationSettings(
                          mode: widget.mode,
                          onSettingsChanged: (settings) {
                            ref.read(visualizationControllerProvider.notifier).updateSettings(settings);
                          },
                        ),
                      ),
                      
                      // 性能优化选项卡
                      SingleChildScrollView(
                        child: Column(
                          children: [
                            OptimizationSettingsWidget(),
                            Divider(),
                            PerformanceMonitorWidget(),
                          ],
                        ),
                      ),
                      
                      // 自动优化选项卡
                      SingleChildScrollView(
                        child: Column(
                          children: [
                            AutoOptimizationSettingsWidget(),
                            Divider(),
                            PerformanceReportWidget(),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: Text('关闭'),
            ),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    // 停止性能分析器
    if (_unityController != null) {
      ref.read(visualizationProfilerProvider(_unityController).notifier).stopProfiling();
    }
    
    _unityController?.dispose();
    // 停止性能监控
    ref.read(performanceMonitorProvider.notifier).stopMonitoring();
    super.dispose();
  }
}