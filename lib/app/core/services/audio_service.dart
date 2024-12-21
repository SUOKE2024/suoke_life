import 'package:just_audio/just_audio.dart';
import 'package:get/get.dart';

class AudioService extends GetxService {
  late AudioPlayer _player;
  
  Future<void> initialize() async {
    _player = AudioPlayer();
  }
  
  Future<void> play(String url) async {
    await _player.setUrl(url);
    await _player.play();
  }
  
  Future<void> pause() async {
    await _player.pause();
  }
  
  Future<void> stop() async {
    await _player.stop();
  }
  
  @override
  void onClose() {
    _player.dispose();
    super.onClose();
  }
} 