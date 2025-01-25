import 'package:flutter/material.dart';
import 'package:suoke_life/ui_components/navigation/bottom_navigation_bar.dart';
import 'package:suoke_life/features/suoke/lib/widgets/service_card.dart';
import 'package:suoke_life/core/utils/app_localizations.dart';

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
    final localizations = AppLocalizations.of(context)!;
    return Scaffold(
      appBar: AppBar(
        title: Text(localizations.translate('suoke_title')),
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: TextField(
              controller: _searchController,
              decoration: InputDecoration(
                hintText: localizations.translate('search_services'),
                prefixIcon: const Icon(Icons.search),
                border: const OutlineInputBorder(),
              ),
              onChanged: _filterServices,
            ),
          ),
          Expanded(
            child: ListView.builder(
              itemCount: _filteredServices.length,
              itemBuilder: (context, index) {
                final service = _filteredServices[index];
                return ServiceCard(
                  title: service.title,
                  description: service.description,
                  imageUrl: service.imageUrl,
                );
              },
            ),
          ),
        ],
      ),
      bottomNavigationBar: AppBottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: _onTabTapped,
      ),
    );
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