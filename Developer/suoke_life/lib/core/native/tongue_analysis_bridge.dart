import 'dart:convert';
import 'dart:ffi';
import 'dart:io';
import 'dart:typed_data';

import 'package:ffi/ffi.dart';
import 'package:flutter/foundation.dart';

/// 舌质类型
enum TongueBodyType {
  pale,        // 淡白舌
  light,       // 淡舌
  pink,        // 淡红舌
  red,         // 红舌
  crimson,     // 绛舌
  purple,      // 紫舌
  blueishPurple, // 青紫舌
  reddish,     // 偏红舌
}

/// 舌苔类型
enum TongueCoatingType {
  thin,        // 薄苔
  thick,       // 厚苔
  white,       // 白苔
  yellow,      // 黄苔
  gray,        // 灰苔
  black,       // 黑苔
  greasy,      // 腻苔
  dry,         // 干苔
  peeled,      // 剥苔
  mirror,      // 镜面舌（无苔）
}

/// 舌形状类型
enum TongueShapeType {
  normal,      // 正常舌
  swollen,     // 胖大舌
  thin,        // 瘦薄舌
  cracked,     // 裂纹舌
  tooth,       // 齿痕舌
  spotted,     // 点刺舌
  trembling,   // 颤动舌
}

/// 舌像分析结果
class TongueAnalysisResult {
  final TongueBodyType bodyType;
  final TongueCoatingType coatingType;
  final TongueShapeType shapeType;
  final double moistureLevel;
  final double vitalityScore;
  final double confidenceScore;
  
  TongueAnalysisResult({
    required this.bodyType,
    required this.coatingType,
    required this.shapeType,
    required this.moistureLevel,
    required this.vitalityScore,
    required this.confidenceScore,
  });
  
  factory TongueAnalysisResult.fromJson(Map<String, dynamic> json) {
    return TongueAnalysisResult(
      bodyType: TongueBodyType.values[json['body_type'] as int],
      coatingType: TongueCoatingType.values[json['coating_type'] as int],
      shapeType: TongueShapeType.values[json['shape_type'] as int],
      moistureLevel: json['moisture_level'] as double,
      vitalityScore: json['vitality_score'] as double,
      confidenceScore: json['confidence_score'] as double,
    );
  }
}

/// Rust舌像分析模块的FFI接口
class TongueAnalysisBridge {
  static final TongueAnalysisBridge _instance = TongueAnalysisBridge._internal();
  factory TongueAnalysisBridge() => _instance;
  
  TongueAnalysisBridge._internal();
  
  late final DynamicLibrary _nativeLib;
  late final _AnalyzeTongueImageFunc _analyzeFunc;
  late final _FreeTongueAnalysisResultFunc _freeFunc;
  
  bool _initialized = false;
  
  /// 初始化桥接
  void initialize() {
    if (_initialized) return;
    
    final libraryPath = _getLibraryPath();
    _nativeLib = DynamicLibrary.open(libraryPath);
    
    _analyzeFunc = _nativeLib
        .lookup<NativeFunction<_AnalyzeTongueImageNative>>('analyze_tongue_image')
        .asFunction<_AnalyzeTongueImageFunc>();
        
    _freeFunc = _nativeLib
        .lookup<NativeFunction<_FreeTongueAnalysisResultNative>>('free_tongue_analysis_result')
        .asFunction<_FreeTongueAnalysisResultFunc>();
        
    _initialized = true;
  }
  
  /// 分析舌像
  Future<TongueAnalysisResult> analyzeTongueImage(Uint8List imageData) async {
    if (!_initialized) initialize();
    
    return compute(_analyzeImageIsolate, _AnalysisParams(
      analyzeFunc: _analyzeFunc,
      freeFunc: _freeFunc,
      imageData: imageData,
    ));
  }
  
  /// 获取对应平台的动态库路径
  String _getLibraryPath() {
    if (Platform.isAndroid) {
      return 'libtongue_analysis.so';
    } else if (Platform.isIOS) {
      return 'tongue_analysis.framework/tongue_analysis';
    } else if (Platform.isMacOS) {
      return 'libtongue_analysis.dylib';
    } else if (Platform.isWindows) {
      return 'tongue_analysis.dll';
    } else if (Platform.isLinux) {
      return 'libtongue_analysis.so';
    } else {
      throw UnsupportedError('平台不支持: ${Platform.operatingSystem}');
    }
  }
}

/// 在独立isolate中处理图像分析
Future<TongueAnalysisResult> _analyzeImageIsolate(_AnalysisParams params) async {
  final imageData = params.imageData;
  final analyzeFunc = params.analyzeFunc;
  final freeFunc = params.freeFunc;
  
  // 分配内存存放图像数据
  final dataPtr = calloc<Uint8>(imageData.length);
  final pointerList = dataPtr.asTypedList(imageData.length);
  pointerList.setAll(0, imageData);
  
  // 结果指针
  final resultPtrPtr = calloc<Pointer<Uint8>>();
  final resultLenPtr = calloc<IntPtr>();
  
  try {
    // 调用Rust函数
    final resultCode = analyzeFunc(
      dataPtr,
      imageData.length,
      resultPtrPtr,
      resultLenPtr,
    );
    
    if (resultCode != 0) {
      throw Exception('舌像分析失败，错误码: $resultCode');
    }
    
    // 获取结果
    final resultPtr = resultPtrPtr.value;
    final resultLen = resultLenPtr.value;
    
    // 将结果转换为Dart字符串
    final resultBytes = resultPtr.asTypedList(resultLen);
    final resultJson = String.fromCharCodes(resultBytes);
    
    // 解析JSON
    final Map<String, dynamic> resultMap = 
        Map<String, dynamic>.from(jsonDecode(resultJson) as Map);
    
    // 释放Rust分配的内存
    freeFunc(resultPtr);
    
    return TongueAnalysisResult.fromJson(resultMap);
  } finally {
    // 释放分配的内存
    calloc.free(dataPtr);
    calloc.free(resultPtrPtr);
    calloc.free(resultLenPtr);
  }
}

/// 分析参数
class _AnalysisParams {
  final _AnalyzeTongueImageFunc analyzeFunc;
  final _FreeTongueAnalysisResultFunc freeFunc;
  final Uint8List imageData;
  
  _AnalysisParams({
    required this.analyzeFunc,
    required this.freeFunc,
    required this.imageData,
  });
}

/// 本地函数类型定义
typedef _AnalyzeTongueImageNative = Int32 Function(
  Pointer<Uint8> dataPtr,
  IntPtr dataLen,
  Pointer<Pointer<Uint8>> resultPtr,
  Pointer<IntPtr> resultLen,
);

typedef _AnalyzeTongueImageFunc = int Function(
  Pointer<Uint8> dataPtr,
  int dataLen,
  Pointer<Pointer<Uint8>> resultPtr,
  Pointer<IntPtr> resultLen,
);

typedef _FreeTongueAnalysisResultNative = Void Function(
  Pointer<Uint8> ptr,
);

typedef _FreeTongueAnalysisResultFunc = void Function(
  Pointer<Uint8> ptr,
); 