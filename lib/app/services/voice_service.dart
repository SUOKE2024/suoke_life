import 'package:get/get.dart';
import 'package:record/record.dart';
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart' as path;

class VoiceService extends GetxService {
  late final AudioRecorder _recorder;
  final isRecording = false.obs;

  Future<VoiceService> init() async {
    _recorder = AudioRecorder();
    return this;
  }

  Future<void> startRecording() async {
    if (await _recorder.hasPermission()) {
      final dir = await getTemporaryDirectory();
      final filePath = path.join(dir.path, '${DateTime.now().millisecondsSinceEpoch}.m4a');
      
      await _recorder.start(
        const RecordConfig(
          encoder: AudioEncoder.aacLc,
          bitRate: 128000,
          sampleRate: 44100,
        ),
        path: filePath,
      );
      isRecording.value = true;
    }
  }

  Future<String?> stopRecording() async {
    final path = await _recorder.stop();
    isRecording.value = false;
    return path;
  }

  @override
  void onClose() {
    _recorder.dispose();
    super.onClose();
  }
} 