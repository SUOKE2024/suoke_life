import 'dart:async';
import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'biometric_analysis_service.dart';

class VisualizationData {
  final String id;
  final String title;
  final DateTime timestamp;
  final List<FlSpot> dataPoints;
  final Color color;
  final String? unit;

  VisualizationData({
    required this.id,
    required this.title,
    required this.timestamp,
    required this.dataPoints,
    required this.color,
    this.unit,
  });
}

class RealtimeVisualizationService {
  final BiometricAnalysisService _analysisService;
  final int _maxDataPoints;
  final Duration _updateInterval;
  
  final StreamController<List<VisualizationData>> _visualizationController = 
      StreamController<List<VisualizationData>>.broadcast();

  final Map<BiometricType, List<FlSpot>> _dataBuffer = {};
  final Map<BiometricType, Color> _typeColors = {
    BiometricType.face: Colors.blue,
    BiometricType.voice: Colors.green,
    BiometricType.emotion: Colors.orange,
    BiometricType.gesture: Colors.purple,
    BiometricType.expression: Colors.red,
  };

  Timer? _updateTimer;
  bool _isVisualizing = false;

  RealtimeVisualizationService({
    required BiometricAnalysisService analysisService,
    int maxDataPoints = 100,
    Duration updateInterval = const Duration(milliseconds: 500),
  }) : _analysisService = analysisService,
       _maxDataPoints = maxDataPoints,
       _updateInterval = updateInterval {
    _initializeVisualization();
  }

  void _initializeVisualization() {
    // 订阅分析结果
    _analysisService.analysisStream.listen((result) {
      if (_isVisualizing) {
        _processAnalysisResult(result);
      }
    });
  }

  void _processAnalysisResult(BiometricAnalysisResult result) {
    // 获取当前时间戳作为X轴
    final timeStamp = DateTime.now().millisecondsSinceEpoch.toDouble();
    
    // 根据不同类型处理数据
    switch (result.type) {
      case BiometricType.face:
        _addDataPoint(
          result.type,
          FlSpot(timeStamp, result.confidence),
        );
        break;
      case BiometricType.voice:
        _addDataPoint(
          result.type,
          FlSpot(timeStamp, result.confidence),
        );
        break;
      case BiometricType.emotion:
        // 情绪数据可能有多个维度
        final emotions = result.analysis['emotions'] as Map<String, double>;
        emotions.forEach((emotion, value) {
          _addDataPoint(
            result.type,
            FlSpot(timeStamp, value),
            subType: emotion,
          );
        });
        break;
      default:
        break;
    }
  }

  void _addDataPoint(
    BiometricType type,
    FlSpot dataPoint, {
    String? subType,
  }) {
    final key = subType != null ? '${type.toString()}_$subType' : type.toString();
    
    _dataBuffer.putIfAbsent(type, () => []).add(dataPoint);

    // 保持数据点数量在限制范围内
    if (_dataBuffer[type]!.length > _maxDataPoints) {
      _dataBuffer[type]!.removeAt(0);
    }

    // 触发更新
    _updateVisualization();
  }

  void _updateVisualization() {
    if (!_isVisualizing) return;

    final visualizations = <VisualizationData>[];

    _dataBuffer.forEach((type, dataPoints) {
      visualizations.add(
        VisualizationData(
          id: type.toString(),
          title: _getTypeTitle(type),
          timestamp: DateTime.now(),
          dataPoints: List.from(dataPoints),
          color: _typeColors[type] ?? Colors.grey,
          unit: _getTypeUnit(type),
        ),
      );
    });

    _visualizationController.add(visualizations);
  }

  String _getTypeTitle(BiometricType type) {
    switch (type) {
      case BiometricType.face:
        return '人脸识别置��度';
      case BiometricType.voice:
        return '声纹识别置信度';
      case BiometricType.emotion:
        return '情绪分析';
      case BiometricType.gesture:
        return '手势识别';
      case BiometricType.expression:
        return '表情识别';
      default:
        return '未知类型';
    }
  }

  String? _getTypeUnit(BiometricType type) {
    switch (type) {
      case BiometricType.face:
      case BiometricType.voice:
      case BiometricType.emotion:
        return '%';
      default:
        return null;
    }
  }

  void startVisualization() {
    if (_isVisualizing) return;
    _isVisualizing = true;

    // 启动定时更新
    _updateTimer = Timer.periodic(_updateInterval, (_) {
      _updateVisualization();
    });
  }

  void stopVisualization() {
    _isVisualizing = false;
    _updateTimer?.cancel();
    _updateTimer = null;
    _dataBuffer.clear();
  }

  // 生成图表数据
  LineChartData generateChartData(VisualizationData data) {
    return LineChartData(
      gridData: FlGridData(show: true),
      titlesData: FlTitlesData(
        bottomTitles: SideTitles(
          showTitles: true,
          reservedSize: 22,
          getTextStyles: (context, value) => const TextStyle(
            color: Colors.grey,
            fontSize: 12,
          ),
          getTitles: (value) {
            final date = DateTime.fromMillisecondsSinceEpoch(value.toInt());
            return '${date.hour}:${date.minute}:${date.second}';
          },
          margin: 8,
        ),
        leftTitles: SideTitles(
          showTitles: true,
          getTextStyles: (context, value) => const TextStyle(
            color: Colors.grey,
            fontSize: 12,
          ),
          getTitles: (value) => '${value.toInt()}${data.unit ?? ''}',
          reservedSize: 28,
          margin: 12,
        ),
      ),
      borderData: FlBorderData(
        show: true,
        border: Border.all(color: Colors.grey.withOpacity(0.5)),
      ),
      minX: data.dataPoints.first.x,
      maxX: data.dataPoints.last.x,
      minY: 0,
      maxY: 100,
      lineBarsData: [
        LineChartBarData(
          spots: data.dataPoints,
          isCurved: true,
          colors: [data.color],
          barWidth: 2,
          isStrokeCapRound: true,
          dotData: FlDotData(show: false),
          belowBarData: BarAreaData(
            show: true,
            colors: [data.color.withOpacity(0.1)],
          ),
        ),
      ],
    );
  }

  void dispose() {
    stopVisualization();
    _visualizationController.close();
  }

  // Getters
  bool get isVisualizing => _isVisualizing;
  Stream<List<VisualizationData>> get visualizationStream => 
      _visualizationController.stream;
} 