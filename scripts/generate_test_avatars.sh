#!/bin/bash

# 创建资源目录
mkdir -p assets/images

# 使用 magick 命令生成测试头像
magick -size 100x100 xc:skyblue -pointsize 40 -gravity center -draw "text 0,0 '小艾'" assets/images/xiaoai_avatar.png
magick -size 100x100 xc:lightgreen -pointsize 40 -gravity center -draw "text 0,0 '老克'" assets/images/laoke_avatar.png
magick -size 100x100 xc:lightpink -pointsize 40 -gravity center -draw "text 0,0 '小克'" assets/images/xiaoke_avatar.png
magick -size 100x100 xc:gray -pointsize 40 -gravity center -draw "text 0,0 'AI'" assets/images/default_avatar.png 