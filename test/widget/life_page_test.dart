import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:bloc_test/bloc_test.dart';
import 'package:suoke_app/app/presentation/pages/life/life_page.dart';
import 'package:suoke_app/app/presentation/blocs/life/life_bloc.dart';
import 'package:suoke_app/app/presentation/blocs/life/life_event.dart';
import 'package:suoke_app/app/presentation/blocs/life/life_state.dart';

class MockLifeBloc extends MockBloc<LifeEvent, LifeState> implements LifeBloc {
  @override
  LifeState get state => const LifeLoading();
}

void main() {
  late MockLifeBloc mockLifeBloc;

  setUp(() {
    mockLifeBloc = MockLifeBloc();
  });

  testWidgets('renders loading state', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: BlocProvider<LifeBloc>.value(
          value: mockLifeBloc,
          child: const LifePage(),
        ),
      ),
    );

    await tester.pump(const Duration(milliseconds: 100));
    expect(find.byType(CircularProgressIndicator), findsOneWidget);
  });
} 