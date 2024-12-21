class LifePage extends StatelessWidget {
  final List<LifeItem> features = [
    LifeItem(
      title: '用户画像',
      icon: Icons.face,
      page: UserProfilePage(),
    ),
    LifeItem(
      title: '健康建议',
      icon: Icons.health_and_safety,
      page: HealthAdvicePage(),
    ),
    LifeItem(
      title: '生活记录',
      icon: Icons.calendar_today,
      page: LifeRecordPage(),
    ),
    LifeItem(
      title: '效果追踪',
      icon: Icons.track_changes,
      page: ProgressTrackingPage(),
    ),
    // ... 其他生活功能
  ];

  // 右下角小克助手气泡
  Widget buildAIAssistant() => AIAssistantBubble(
    avatar: 'xiaoke.png',
    onTap: () => Get.to(XiaokeAssistantPage()),
  );
} 