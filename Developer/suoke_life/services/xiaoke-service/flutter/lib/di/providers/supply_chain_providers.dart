import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/network/api_client.dart';
import '../../data/repositories/traceability_repository.dart';
import '../../data/models/supply_chain_model.dart';

final apiClientProvider = Provider<ApiClient>((ref) {
  return ApiClient();
});

final traceabilityRepositoryProvider = Provider<TraceabilityRepository>((ref) {
  final apiClient = ref.watch(apiClientProvider);
  return TraceabilityRepository(apiClient);
});

final riskPredictionProvider = FutureProvider.family<List<SupplyChainRiskModel>, String>(
  (ref, productId) async {
    final repository = ref.read(traceabilityRepositoryProvider);
    return repository.getRiskPredictions(productId);
  }
);