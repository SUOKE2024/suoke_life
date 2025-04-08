import 'package:auto_route/auto_route.dart';
import 'package:suoke_life/core/widgets/tcm/pulse/pulse_diagnosis_widget.dart';
import 'package:suoke_life/core/widgets/tcm/tongue/tongue_diagnosis_widget.dart';
import 'package:suoke_life/presentation/tcm/tcm_diagnosis_page.dart';
import 'package:suoke_life/presentation/suoke/pages/suoke_page.dart';
import 'package:suoke_life/presentation/suoke/pages/tcm_features_page.dart';

/// TCM相关路由配置
class TcmRoutes {
  // 私有构造函数，防止实例化
  TcmRoutes._();

  // 脉诊路由
  static const String pulseDiagnosisPath = '/tcm/pulse-diagnosis';
  static const String pulseDiagnosisName = 'PulseDiagnosisRoute';

  // 舌诊路由
  static const String tongueDiagnosisPath = '/tcm/tongue-diagnosis';
  static const String tongueDiagnosisName = 'TongueDiagnosisRoute';
  
  // 多模态诊断路由
  static const String multimodalDiagnosisPath = '/tcm/multimodal-diagnosis';
  static const String multimodalDiagnosisName = 'TcmDiagnosisRoute';
  
  // 中医特色功能入口路由
  static const String tcmFeaturesPath = '/tcm/features';
  static const String tcmFeaturesName = 'TcmFeaturesRoute';
  
  // 路由列表
  static final List<AutoRoute> routes = [
    AutoRoute(
      path: pulseDiagnosisPath,
      page: PulseDiagnosisRoute.page,
    ),
    AutoRoute(
      path: tongueDiagnosisPath,
      page: TongueDiagnosisRoute.page,
    ),
    AutoRoute(
      path: multimodalDiagnosisPath,
      page: TcmDiagnosisRoute.page,
    ),
    AutoRoute(
      path: tcmFeaturesPath,
      page: TcmFeaturesRoute.page,
    ),
  ];
}
