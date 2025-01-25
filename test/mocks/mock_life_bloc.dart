import 'package:bloc_test/bloc_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:suoke_app/app/presentation/blocs/life/life_bloc.dart';

class MockLifeBloc extends MockBloc<LifeEvent, LifeState> 
    implements LifeBloc {
  MockLifeBloc() {
    when(() => state).thenAnswer((_) => const LifeState(isLoading: true));
  }
} 