abstract class NavigationState {
  const NavigationState();
}

class NavigationInitial extends NavigationState {
  const NavigationInitial();
}

class NavigationLoaded extends NavigationState {
  final int currentTab;
  final String currentRoute;
  final List<String> history;

  const NavigationLoaded({
    this.currentTab = 0,
    this.currentRoute = '/',
    this.history = const [],
  });

  NavigationLoaded copyWith({
    int? currentTab,
    String? currentRoute,
    List<String>? history,
  }) {
    return NavigationLoaded(
      currentTab: currentTab ?? this.currentTab,
      currentRoute: currentRoute ?? this.currentRoute,
      history: history ?? this.history,
    );
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is NavigationLoaded &&
          runtimeType == other.runtimeType &&
          currentTab == other.currentTab &&
          currentRoute == other.currentRoute &&
          history == other.history;

  @override
  int get hashCode =>
      currentTab.hashCode ^ currentRoute.hashCode ^ history.hashCode;
} 