import 'package:flutter/material.dart';
import 'package:suoke_life/ui_components/navigation/bottom_navigation_bar.dart';
import 'package:suoke_life/features/suoke/lib/widgets/service_card.dart';
import 'package:suoke_life/lib/core/utils/app_localizations.dart';
import 'package:suoke_life/lib/core/widgets/common_bottom_navigation_bar.dart';

class SuokePage extends StatefulWidget {
  const SuokePage({Key? key}) : super(key: key);

  @override
  State<SuokePage> createState() => _SuokePageState();
}

class _SuokePageState extends State<SuokePage> {
  int _currentIndex = 1;
  final List<Service> _services = [
    Service(
      title: 'Yoga Class',
      description: 'Improve your flexibility and strength.',
      imageUrl: 'assets/images/yoga.jpg',
    ),
    Service(
      title: 'Massage Therapy',
      description: 'Relax and rejuvenate with a massage.',
      imageUrl: 'assets/images/massage.jpg',
    ),
    Service(
      title: 'Meditation Session',
      description: 'Find inner peace with a guided meditation.',
      imageUrl: 'assets/images/meditation.jpg',
    ),
    Service(
      title: 'Personal Training',
      description: 'Get personalized fitness guidance.',
      imageUrl: 'assets/images/training.jpg',
    ),
    Service(
      title: 'Nutrition Consultation',
      description: 'Get expert advice on healthy eating.',
      imageUrl: 'assets/images/nutrition.jpg',
    ),
  ];
  List<Service> _filteredServices = [];
  final TextEditingController _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _filteredServices = _services;
  }

  void _onTabTapped(int index) {
    setState(() {
      _currentIndex = index;
    });
  }

  void _filterServices(String query) {
    setState(() {
      _filteredServices = _services
          .where((service) =>
              service.title.toLowerCase().contains(query.toLowerCase()) ||
              service.description.toLowerCase().contains(query.toLowerCase()))
          .toList();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(AppLocalizations.of(context)!.translate('suoke_services') ?? 'SUOKE Services'),
      ),
      body: ListView.builder(
        itemCount: _services.length,
        itemBuilder: (context, index) {
          final service = _services[index];
          return ServiceCard(
            title: service.title,
            description: service.description,
            imageUrl: service.imageUrl,
            onTap: () {
              Navigator.pushNamed(context, '/serviceDetail', arguments: service);
            },
          );
        },
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          _generateContent();
        },
        child: const Icon(Icons.add),
      ),
      bottomNavigationBar: CommonBottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) {
          setState(() {
            _currentIndex = index;
            // TODO: 实现底部导航逻辑
          });
        },
      ),
    );
  }

  void _generateContent() {
    // TODO: 实现内容生成逻辑
    print('内容生成成功');
  }
}

class Service {
  final String title;
  final String description;
  final String imageUrl;

  Service({
    required this.title,
    required this.description,
    required this.imageUrl,
  });
} 