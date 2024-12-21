import 'package:get/get.dart';
import '../../services/call_service.dart';
import '../../data/models/user.dart';
import 'package:agora_rtc_engine/agora_rtc_engine.dart';

class CallController extends GetxController {
  final CallService _callService;
  final String channelId;
  final User peer;
  final bool isVideo;

  final isJoined = false.obs;
  final isMuted = false.obs;
  final isSpeakerOn = false.obs;
  final isVideoEnabled = true.obs;
  final callDuration = 0.obs;
  final remoteUid = 0.obs;

  RtcEngine? _engine;
  Timer? _timer;

  CallController({
    required CallService callService,
    required this.channelId,
    required this.peer,
    required this.isVideo,
  }) : _callService = callService;

  @override
  void onInit() {
    super.onInit();
    _initAgoraEngine();
  }

  @override
  void onClose() {
    _timer?.cancel();
    _engine?.leaveChannel();
    _engine?.release();
    super.onClose();
  }

  Future<void> _initAgoraEngine() async {
    try {
      _engine = await RtcEngine.createWithContext(RtcEngineContext(
        _callService.agoraAppId,
      ));

      await _engine?.enableVideo();
      await _engine?.setChannelProfile(ChannelProfile.Communication);
      await _engine?.setClientRole(ClientRole.Broadcaster);

      _engine?.setEventHandler(RtcEngineEventHandler(
        joinChannelSuccess: (channel, uid, elapsed) {
          isJoined.value = true;
          _startTimer();
        },
        userJoined: (uid, elapsed) {
          remoteUid.value = uid;
        },
        userOffline: (uid, reason) {
          if (uid == remoteUid.value) {
            remoteUid.value = 0;
            Get.back();
          }
        },
        error: (code) {
          debugPrint('Agora error: $code');
        },
      ));

      await _joinChannel();
    } catch (e) {
      debugPrint('初始化通话引擎失败: $e');
    }
  }

  Future<void> _joinChannel() async {
    try {
      final token = await _callService.getToken(channelId);
      await _engine?.joinChannel(
        token,
        channelId,
        null,
        0,
      );
    } catch (e) {
      debugPrint('加入通话失败: $e');
    }
  }

  void _startTimer() {
    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      callDuration.value++;
    });
  }

  void toggleMute() {
    isMuted.value = !isMuted.value;
    _engine?.muteLocalAudioStream(isMuted.value);
  }

  void toggleSpeaker() {
    isSpeakerOn.value = !isSpeakerOn.value;
    _engine?.setEnableSpeakerphone(isSpeakerOn.value);
  }

  void toggleVideo() {
    isVideoEnabled.value = !isVideoEnabled.value;
    _engine?.muteLocalVideoStream(!isVideoEnabled.value);
  }

  void switchCamera() {
    _engine?.switchCamera();
  }

  void endCall() {
    _engine?.leaveChannel();
    Get.back();
  }

  String get formattedDuration {
    final duration = Duration(seconds: callDuration.value);
    return '${duration.inMinutes.toString().padLeft(2, '0')}:${(duration.inSeconds % 60).toString().padLeft(2, '0')}';
  }
} 