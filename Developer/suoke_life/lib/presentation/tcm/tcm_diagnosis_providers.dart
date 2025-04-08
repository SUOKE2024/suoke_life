import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/domain/entities/tcm/tcm_diagnosis_result.dart';
import 'package:suoke_life/domain/repositories/tcm_repository.dart';
import 'package:suoke_life/data/repositories/tcm_repository_impl.dart';
import 'package:suoke_life/di/providers/http_providers.dart';

// TCM Repository Provider
final tcmRepositoryProvider = Provider<TcmRepository>((ref) {
  final dio = ref.watch(dioProvider);
  return TcmRepositoryImpl(dio: dio);
});

// TCM 诊断状态
class TcmDiagnosisState {
  final bool isLoading;
  final TcmDiagnosisResult? diagnosis;
  final Object? error;

  const TcmDiagnosisState({
    this.isLoading = false,
    this.diagnosis,
    this.error,
  });

  bool get hasError => error != null;

  TcmDiagnosisState copyWith({
    bool? isLoading,
    TcmDiagnosisResult? diagnosis,
    Object? error,
  }) {
    return TcmDiagnosisState(
      isLoading: isLoading ?? this.isLoading,
      diagnosis: diagnosis ?? this.diagnosis,
      error: error,
    );
  }
}

// TCM 诊断控制器
class TcmDiagnosisController extends StateNotifier<TcmDiagnosisState> {
  final TcmRepository _repository;

  TcmDiagnosisController({required TcmRepository repository})
      : _repository = repository,
        super(const TcmDiagnosisState());

  Future<void> submitDiagnosis({
    String? tongueImage,
    String? faceImage,
    String? audioData,
    String? description,
  }) async {
    try {
      state = state.copyWith(isLoading: true, error: null);

      final result = await _repository.submitMultimodalDiagnosis(
        tongueImage: tongueImage,
        faceImage: faceImage,
        audioData: audioData,
        description: description,
      );

      state = state.copyWith(isLoading: false, diagnosis: result);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e);
    }
  }

  void reset() {
    state = const TcmDiagnosisState();
  }
}

// TCM 诊断控制器 Provider
final tcmDiagnosisControllerProvider =
    StateNotifierProvider<TcmDiagnosisController, TcmDiagnosisState>((ref) {
  final repository = ref.watch(tcmRepositoryProvider);
  return TcmDiagnosisController(repository: repository);
});