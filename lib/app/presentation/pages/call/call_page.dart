import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/call_controller.dart';
import 'package:agora_rtc_engine/agora_rtc_engine.dart';

class CallPage extends StatelessWidget {
  const CallPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: SafeArea(
        child: Stack(
          children: [
            // 视频区域
            if (controller.isVideo) ...[
              Center(
                child: Obx(() {
                  if (controller.remoteUid.value != 0) {
                    return AgoraVideoView(
                      controller: VideoViewController.remote(
                        rtcEngine: controller._engine!,
                        canvas: VideoCanvas(uid: controller.remoteUid.value),
                        connection: RtcConnection(
                          channelId: controller.channelId,
                        ),
                      ),
                    );
                  }
                  return const Center(child: CircularProgressIndicator());
                }),
              ),
              Positioned(
                right: 16,
                top: 16,
                child: Container(
                  width: 120,
                  height: 160,
                  decoration: BoxDecoration(
                    border: Border.all(color: Colors.white),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(8),
                    child: AgoraVideoView(
                      controller: VideoViewController(
                        rtcEngine: controller._engine!,
                        canvas: const VideoCanvas(uid: 0),
                      ),
                    ),
                  ),
                ),
              ),
            ],

            // 用户信息
            Positioned(
              top: 24,
              left: 0,
              right: 0,
              child: Column(
                children: [
                  CircleAvatar(
                    radius: 30,
                    backgroundImage: NetworkImage(controller.peer.avatar),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    controller.peer.name,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Obx(() => Text(
                    controller.isJoined.value
                        ? controller.formattedDuration
                        : '正在连接...',
                    style: const TextStyle(
                      color: Colors.white70,
                      fontSize: 14,
                    ),
                  )),
                ],
              ),
            ),

            // 控制按钮
            Positioned(
              bottom: 48,
              left: 0,
              right: 0,
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  _buildControlButton(
                    icon: Icons.mic_off,
                    isEnabled: controller.isMuted,
                    onPressed: controller.toggleMute,
                  ),
                  if (controller.isVideo)
                    _buildControlButton(
                      icon: Icons.switch_camera,
                      onPressed: controller.switchCamera,
                    ),
                  _buildControlButton(
                    icon: Icons.call_end,
                    backgroundColor: Colors.red,
                    onPressed: controller.endCall,
                  ),
                  _buildControlButton(
                    icon: Icons.volume_up,
                    isEnabled: controller.isSpeakerOn,
                    onPressed: controller.toggleSpeaker,
                  ),
                  if (controller.isVideo)
                    _buildControlButton(
                      icon: Icons.videocam_off,
                      isEnabled: !controller.isVideoEnabled,
                      onPressed: controller.toggleVideo,
                    ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildControlButton({
    required IconData icon,
    bool isEnabled = false,
    Color? backgroundColor,
    required VoidCallback onPressed,
  }) {
    return Container(
      width: 56,
      height: 56,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: backgroundColor ?? (isEnabled ? Colors.white : Colors.white24),
      ),
      child: IconButton(
        icon: Icon(icon),
        color: backgroundColor != null
            ? Colors.white
            : (isEnabled ? Colors.black : Colors.white),
        onPressed: onPressed,
      ),
    );
  }
} 