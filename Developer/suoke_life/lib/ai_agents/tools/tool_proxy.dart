import 'package:suoke_life/ai_agents/tools/tool_interface.dart';
import 'package:suoke_life/core/network/api_client.dart';

class ToolProxy implements Tool {
  final String _name;
  final String _description;
  final List<ToolParameterDefinition> _parameters;
  final ApiClient _apiClient;
  final bool _requiresAuthentication;
  
  ToolProxy({
    required String name,
    required String description,
    required List<ToolParameterDefinition> parameters,
    required ApiClient apiClient,
    required bool requiresAuthentication,
  }) : 
    _name = name,
    _description = description,
    _parameters = parameters,
    _apiClient = apiClient,
    _requiresAuthentication = requiresAuthentication;
  
  @override
  String get name => _name;
  
  @override
  String get description => _description;
  
  @override
  List<ToolParameterDefinition> get parameters => _parameters;
  
  @override
  bool get requiresAuthentication => _requiresAuthentication;
  
  @override
  Future<ToolCallResult> execute(Map<String, dynamic> parameters, String callId) async {
    try {
      final response = await _apiClient.executeToolCall(_name, parameters);
      
      if (response.containsKey('error')) {
        return ToolCallResult.error(
          callId,
          response['error'] ?? '工具调用失败',
        );
      }
      
      return ToolCallResult.success(
        callId,
        response['data'],
      );
    } catch (e) {
      return ToolCallResult.error(
        callId,
        '工具调用异常: ${e.toString()}',
      );
    }
  }
}
