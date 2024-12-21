import 'package:flutter/material.dart';
import 'package:get/get.dart';

class CustomBottomNavigationBar extends StatelessWidget {
  final int currentIndex;
  final ValueChanged<int> onTap;
  final List<BottomNavigationBarItem> items;

  const CustomBottomNavigationBar({
    Key? key,
    required this.currentIndex,
    required this.onTap,
    required this.items,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return BottomAppBar(
      shape: const CircularNotchedRectangle(),
      notchMargin: 8,
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: List.generate(items.length, (index) {
          final item = items[index];
          final isSelected = currentIndex == index;
          
          return Expanded(
            child: InkWell(
              onTap: () => onTap(index),
              child: Container(
                height: 56,
                padding: const EdgeInsets.symmetric(vertical: 8),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      isSelected ? item.activeIcon.icon : item.icon.icon,
                      color: isSelected ? Get.theme.primaryColor : Colors.grey,
                    ),
                    const SizedBox(height: 4),
                    Text(
                      item.label!,
                      style: TextStyle(
                        fontSize: 12,
                        color: isSelected ? Get.theme.primaryColor : Colors.grey,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          );
        }),
      ),
    );
  }
} 