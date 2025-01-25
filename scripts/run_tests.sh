#!/bin/bash

# 生成 mock 文件
echo "Generating mocks..."
cd libs/core && flutter pub run build_runner build --delete-conflicting-outputs && cd ../..
for dir in apps/*; do
  if [ -d "$dir" ]; then
    echo "Generating mocks in $dir..."
    (cd "$dir" && flutter pub run build_runner build --delete-conflicting-outputs)
  fi
done

# 运行测试
echo "Running tests..."
cd libs/core && flutter test && cd ../..
for dir in apps/*; do
  if [ -d "$dir" ]; then
    echo "Running tests in $dir..."
    (cd "$dir" && flutter test)
  fi
done 