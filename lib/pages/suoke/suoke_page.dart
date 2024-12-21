class SuokePage extends StatelessWidget {
  final List<ServiceItem> services = [
    ServiceItem(
      title: '健康问卷',
      icon: Icons.assignment,
      page: HealthQuestionnairePage(),
    ),
    ServiceItem(
      title: '中医体质检测',
      icon: Icons.healing,
      page: TCMConstitutionPage(),
    ),
    ServiceItem(
      title: '生命体征检测',
      icon: Icons.favorite,
      page: VitalSignsPage(),
    ),
    ServiceItem(
      title: '农产品定制',
      icon: Icons.agriculture,
      page: CustomProductPage(),
    ),
    ServiceItem(
      title: '第三方服务',
      icon: Icons.api,
      page: ThirdPartyServicesPage(),
    ),
    ServiceItem(
      title: '供应链入口',
      icon: Icons.inventory,
      page: SupplyChainPage(),
    ),
  ];

  // 右下角小艾助手气泡
  Widget buildAIAssistant() => AIAssistantBubble(
    avatar: 'xiaoi.png',
    onTap: () => Get.to(XiaoiAssistantPage()),
  );

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('SUOKE')),
      body: Stack(
        children: [
          GridView.count(
            crossAxisCount: 2,
            padding: const EdgeInsets.all(16),
            children: services,
          ),
          buildAIAssistant(),
        ],
      ),
    );
  }
} 