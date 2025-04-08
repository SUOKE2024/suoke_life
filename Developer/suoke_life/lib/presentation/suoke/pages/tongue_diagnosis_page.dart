import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/core/widgets/tcm/tongue/tongue_diagnosis_widget.dart';
import 'package:suoke_life/core/widgets/tcm/models/tongue_diagnosis_data.dart';

/// 舌诊分析页面
@RoutePage()
class TongueDiagnosisPage extends ConsumerWidget {
  /// 外部传入的图片路径
  final String? imagePath;

  /// 创建舌诊分析页面
  const TongueDiagnosisPage({super.key, this.imagePath});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('舌诊智能分析'),
        centerTitle: true,
      ),
      body: SafeArea(
        child: TongueDiagnosisWidget(
          initialImagePath: imagePath,
        ),
      ),
    );
  }
}
