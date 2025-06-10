// 内容类型/;,/g/;
export type ContentType = | "artic;l;";";,"";
e;";"";
  | "video"";"";
  | "course"";"";
  | "recipe"";"";
  | "wisdom"";"";
  | "theory"";"";
// 分类类型"/;,"/g"/;
export type CategoryType = | "t;c;";";,"";
m;";"";
  | "nutrition"";"";
  | "exercise"";"";
  | "mental"";"";
  | "lifestyle"";"";
  | "herbs"";"";
  | "acupoints"";"";
// 难度等级"/;,"/g"/;
export type DifficultyLevel = "beginner" | "intermediate" | "advanc;e;";";,"";
d;
// 内容项接口/;,/g/;
export interface ContentItem {};
const id = string;}
  title: string,;
subtitle: string,;
type: ContentType,;
category: CategoryType,;
author: string,;
readTime: string,;
likes: number,;
image: string,tags: string[],difficulty: DifficultyLevel;
featured?: boolean;
description?: string;
content?: string}
// 分类配置接口/;,/g/;
export interface CategoryConfig {};
const name = string;}
  icon: string,;
color: string,;
const description = string;}
// 热门话题接口/;,/g/;
export interface HotTopic {};
const id = string;}
  title: string,count: number,icon: string;
trending?: boolean}
// 学习进度接口/;,/g/;
export interface LearningProgress {};
const contentId = string;};
userId: string,progress: number;
// 0-100,/;,/g,/;
  completed: boolean,;
lastAccessTime: string,;
const bookmarked = boolean;}
// 搜索过滤器接口"/;,"/g"/;
export interface SearchFilters {"}";
const category = CategoryType | "all";}";,"";
contentType: ContentType | "all";",";
difficulty: DifficultyLevel | "all";",";
author: string,;
const tags = string[];
  ;}
// 探索页面状态接口"/;,"/g"/;
export interface ExploreState {"}";
const selectedCategory = CategoryType | "all";}";,"";
searchQuery: string,;
filters: SearchFilters,;
isLoading: boolean,";,"";
error: string | null,refreshing: boolean;};""";