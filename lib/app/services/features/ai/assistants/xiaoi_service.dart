import 'package:suoke_app/app/core/services/network/network_service.dart';

class XiaoiService {
  final NetworkService _network;

  XiaoiService(this._network);

  Future<void> init() async {
    // 初始化小艾服务
  }

  Future<String> chat(String message) async {
    // 调用小艾 API
    final response = await _network.post(
      'https://api.xiaoi.com/chat',
      data: {'message': message},
    );
    return response['reply'] as String;
  }
} 