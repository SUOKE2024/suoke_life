.PHONY: clean get codegen format test coverage

clean:
	flutter clean
	rm -rf build

get:
	flutter pub get

codegen:
	flutter pub run build_runner build --delete-conflicting-outputs

watch:
	flutter pub run build_runner watch --delete-conflicting-outputs

format:
	dart format lib test

test:
	flutter test

coverage:
	flutter test --coverage
	genhtml coverage/lcov.info -o coverage/html
	open coverage/html/index.html

install:
	make clean
	make get
	make codegen

update:
	flutter pub upgrade
	flutter pub outdated 

build:
	flutter pub get
	flutter pub run build_runner build --delete-conflicting-outputs 