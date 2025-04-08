#!/bin/bash

# 运行单元测试

go clean -testcache && go test -v ./internal/handlers/... 