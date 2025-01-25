import 'package:core/network/multimodal_service_client.dart';
import 'package:backend/apps/multimodal_service/lib/models/media_request.dart';
import 'package:core/models/health_models.dart';
import 'package:core/models/image_data.dart';
import 'package:core/models/pulse_data.dart';

class MultimodalServiceClientImpl implements MultimodalServiceClient {
  const MultimodalServiceClientImpl();

  @override
  Future<BiologicalSignals> getUserData(String userId) async {
    // 实际应调用多模态服务API获取实时数据，此处返回示例数据
    return BiologicalSignals(
      tongueImage: ImageData(url: 'https://api.suoke.life/images/$userId/tongue'),
      pulseWaveform: PulseData(
        waveform: [0.1, 0.3, 0.5, 0.7, 0.9],
        sampleRate: 1000
      )
    );
  }
}
