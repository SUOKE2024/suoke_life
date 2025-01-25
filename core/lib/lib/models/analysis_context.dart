import 'package:core/core.dart';

class AnalysisContext {
  final UserProfile userData;
  final TCMPatterns tcmPatterns;
  final DateTime analysisTime;

  AnalysisContext({
    required this.userData,
    required this.tcmPatterns,
    this.analysisTime = DateTime.now(),
  });
}
