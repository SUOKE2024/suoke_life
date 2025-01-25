import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../services/connectivity_service.dart';

class NetworkStatusIndicator extends StatelessWidget {
  const NetworkStatusIndicator({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final connectivityService = Get.find<ConnectivityService>();

    return Obx(() {
      final isConnected = connectivityService.isConnected.value;
      final connectionType = connectivityService.currentConnectionType;

      return Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color: isConnected ? Colors.green[100] : Colors.red[100],
          borderRadius: BorderRadius.circular(16),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              isConnected ? Icons.wifi : Icons.wifi_off,
              size: 16,
              color: isConnected ? Colors.green[700] : Colors.red[700],
            ),
            const SizedBox(width: 8),
            Text(
              connectionType,
              style: TextStyle(
                fontSize: 12,
                color: isConnected ? Colors.green[700] : Colors.red[700],
              ),
            ),
          ],
        ),
      );
    });
  }
} 