import 'package:dio/dio.dart';
import '../../core/network/api_client.dart';
import '../models/supply_chain_model.dart';

class TraceabilityRepository {
  final ApiClient _apiClient;

  TraceabilityRepository(this._apiClient);

  // 获取产品溯源信息
  Future<ProductTraceabilityModel> getProductTraceability(String qrId) async {
    try {
      final response = await _apiClient.dio.get('/consumer/trace/$qrId');
      return ProductTraceabilityModel.fromJson(response.data['data']);
    } catch (e) {
      throw _handleError(e);
    }
  }
  
  // 验证区块链证明
  Future<Map<String, dynamic>> verifyBlockchainProof(String eventId) async {
    try {
      final response = await _apiClient.dio.get('/blockchain/verify/$eventId');
      return response.data['data'];
    } catch (e) {
      throw _handleError(e);
    }
  }
  
  // 获取风险预测
  Future<List<SupplyChainRiskModel>> getRiskPredictions(String productId) async {
    try {
      final response = await _apiClient.dio.get('/prediction/risks/$productId');
      final List<dynamic> risks = response.data['data']['risks'];
      return risks.map((risk) => SupplyChainRiskModel.fromJson(risk)).toList();
    } catch (e) {
      throw _handleError(e);
    }
  }

  Exception _handleError(dynamic error) {
    if (error is DioError) {
      final errorMessage = error.response?.data?['message'] ?? '网络请求失败';
      return Exception(errorMessage);
    }
    return Exception('未知错误: ${error.toString()}');
  }
}