import 'package:get/get.dart';
import '../doubao_service.dart';

class AiService extends GetxService {
  final DouBaoService _douBaoService;

  AiService({required DouBaoService douBaoService}) 
    : _douBaoService = douBaoService;

  Future<String> chat(String message, {String model = 'xiaoai'}) async {
    try {
      return await _douBaoService.chat(message, model);
    } catch (e) {
      rethrow;
    }
  }
} 