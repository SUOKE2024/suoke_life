class HomeState {
  final int currentIndex;

  const HomeState({this.currentIndex = 0});

  HomeState copyWith({int? currentIndex}) {
    return HomeState(
      currentIndex: currentIndex ?? this.currentIndex,
    );
  }
} 