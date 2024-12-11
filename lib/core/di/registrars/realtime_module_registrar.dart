import 'package:get_it/get_it.dart';
import '../module_registrar.dart';
import '../../../services/realtime_data_collection_service.dart';
import '../../../services/biometric_analysis_service.dart';
import '../../../services/realtime_visualization_service.dart';
import '../../../services/secure_data_transport_service.dart';

/// 实时服务模块注册器
class RealtimeModuleRegistrar implements ModuleRegistrar {
  @override
  String get moduleName => '实时服务模块';
  
  @override
  List<Type> get dependencies => [
    SecureDataTransportService,  // 依赖安全传输服务
  ];

  @override
  Future<void> register(GetIt getIt) async {
    // 验证依赖
    await validateDependencies(getIt);
    
    // 数据采集服务
    getIt.registerLazySingleton(() => RealtimeDataCollectionService());
    
    // 生物特征分析服务
    getIt.registerLazySingleton(() => BiometricAnalysisService());
    
    // 实时可视化服务
    getIt.registerLazySingleton(
      () => RealtimeVisualizationService(
        analysisService: getIt<BiometricAnalysisService>(),
      ),
    );
  }

  @override
  Future<void> registerAsync(GetIt getIt) async {
    // 等待安全传输服务就绪
    await getIt.isReady<SecureDataTransportService>();
    
    // 初始化数据采集服务
    final dataCollection = getIt<RealtimeDataCollectionService>();
    await dataCollection.initialize();
  }

  @override
  Future<void> onModuleReady(GetIt getIt) async {
    // 初始化生物特征分析服务
    final biometricAnalysis = getIt<BiometricAnalysisService>();
    await biometricAnalysis.initialize();
    
    // 初始化实时可视化服务
    final visualization = getIt<RealtimeVisualizationService>();
    await visualization.initialize();
  }

  @override
  Future<void> onModuleDispose(GetIt getIt) async {
    // 清理数据采集服务
    final dataCollection = getIt<RealtimeDataCollectionService>();
    await dataCollection.dispose();
    
    // 清理生物特征分析服务
    final biometricAnalysis = getIt<BiometricAnalysisService>();
    await biometricAnalysis.dispose();
    
    // 清理实时可视化服务
    final visualization = getIt<RealtimeVisualizationService>();
    await visualization.dispose();
  }
} 