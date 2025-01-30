// import 'package:injectable/injectable.dart';
// @injectable
import 'package:suoke_life/lib/core/network/multimodal_service_client.dart';

class MultimodalProcessingService {
  final MultimodalServiceClient _multimodalServiceClient;

  MultimodalProcessingService(this._multimodalServiceClient);

  Future<String> processImage(String imagePath) async {
    final response = await _multimodalServiceClient.processImage(imagePath);
    return 'Processed image data: ${response.data}';
  }
} 