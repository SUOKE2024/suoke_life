import 'package:get/get.dart';
import 'package:record/record.dart';
import 'package:audioplayers/audioplayers.dart';
import 'package:audio_session/audio_session.dart';

class AudioService extends GetxService {
  late Record _recorder;
  late AudioPlayer _player;
  final isRecording = false.obs;
  final isPlaying = false.obs;
  
  Future<void> initialize() async {
    _recorder = Record();
    _player = AudioPlayer();
    
    // 配置音频会话
    final session = await AudioSession.instance;
    await session.configure(const AudioSessionConfiguration(
      avAudioSessionCategory: AVAudioSessionCategory.playAndRecord,
      avAudioSessionCategoryOptions: AVAudioSessionCategoryOptions.allowBluetooth,
      avAudioSessionMode: AVAudioSessionMode.spokenAudio,
      avAudioSessionRouteSharingPolicy: AVAudioSessionRouteSharingPolicy.defaultPolicy,
      avAudioSessionSetActiveOptions: AVAudioSessionSetActiveOptions.none,
    ));
  }
  
  Future<void> startRecording() async {
    try {
      if (await _recorder.hasPermission()) {
        await _recorder.start(
          encoder: AudioEncoder.aacLc,
          bitRate: 128000,
          samplingRate: 44100,
        );
        isRecording.value = true;
      }
    } catch (e) {
      print('Error starting recording: $e');
    }
  }
  
  Future<String?> stopRecording() async {
    try {
      final path = await _recorder.stop();
      isRecording.value = false;
      return path;
    } catch (e) {
      print('Error stopping recording: $e');
      return null;
    }
  }
  
  Future<void> play(String source, {bool isLocal = true}) async {
    try {
      if (isLocal) {
        await _player.play(DeviceFileSource(source));
      } else {
        await _player.play(UrlSource(source));
      }
      isPlaying.value = true;
    } catch (e) {
      print('Error playing audio: $e');
    }
  }
  
  Future<void> pause() async {
    await _player.pause();
    isPlaying.value = false;
  }
  
  Future<void> stop() async {
    await _player.stop();
    isPlaying.value = false;
  }
  
  Future<void> seek(Duration position) async {
    await _player.seek(position);
  }
  
  Stream<Duration> get positionStream => _player.onPositionChanged;
  Stream<Duration?> get durationStream => _player.onDurationChanged;
  
  @override
  void onClose() {
    _recorder.dispose();
    _player.dispose();
    super.onClose();
  }
} 