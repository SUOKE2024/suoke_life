import React from "react";
import {
  ContentItem,
  CategoryConfig,
  HotTopic,
  CategoryType
} from "../types/explore";

// 分类配置
export const CATEGORIES: Record<CategoryType, CategoryConfig> = {
  tcm: {
    name: "中医理论",
    icon: "leaf",
    color: "#34C759",
    description: "传统中医理论与现代应用"
  },
  nutrition: {
    name: "食疗养生",
    icon: "food-apple",
    color: "#FF9500",
    description: "药食同源，食疗养生"
  },
  exercise: {
    name: "运动养生",
    icon: "run",
    color: "#007AFF",
    description: "太极、八段锦等传统运动"
  },
  mental: {
    name: "心神调养",
    icon: "brain",
    color: "#FF2D92",
    description: "情志调节与心神安宁"
  },
  lifestyle: {
    name: "起居养生",
    icon: "home-heart",
    color: "#5856D6",
    description: "顺应自然的生活方式"
  },
  herbs: {
    name: "本草药材",
    icon: "flower",
    color: "#8E44AD",
    description: "中药材识别与应用"
  },
  acupoints: {
    name: "经络穴位",
    icon: "human-handsup",
    color: "#E74C3C",
    description: "经络穴位与按摩保健"
  }
};

// 热门话题
export const HOT_TOPICS: HotTopic[] = [
  {
    id: "wisdom_1",
    title: "春季养生要点",
    category: "lifestyle",
    views: 12580,
    likes: 856,
    comments: 234,
    isHot: true
  },
  {
    id: "wisdom_2", 
    title: "五脏六腑调理法",
    category: "tcm",
    views: 9876,
    likes: 654,
    comments: 189,
    isHot: true
  },
  {
    id: "wisdom_3",
    title: "常用穴位按摩",
    category: "acupoints", 
    views: 8765,
    likes: 543,
    comments: 167,
    isHot: true
  }
];

// 内容数据
export const CONTENT_ITEMS: ContentItem[] = [
  {
    id: "tcm_1",
    title: "阴阳五行理论",
    category: "tcm",
    type: "article",
    author: "小艾",
    publishTime: "2024-01-15",
    readTime: 8,
    views: 1250,
    likes: 89,
    summary: "深入了解中医基础理论中的阴阳五行学说",
    tags: ["基础理论", "阴阳", "五行"],
    difficulty: "beginner"
  },
  {
    id: "nutrition_1", 
    title: "四季食疗养生",
    category: "nutrition",
    type: "video",
    author: "小艾",
    publishTime: "2024-01-20",
    readTime: 15,
    views: 2340,
    likes: 156,
    summary: "根据四季变化调整饮食，达到养生保健的目的",
    tags: ["食疗", "四季养生", "饮食调理"],
    difficulty: "intermediate"
  }
];

export default {
  CATEGORIES,
  HOT_TOPICS,
  CONTENT_ITEMS
};