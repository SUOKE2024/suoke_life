import {

  ContentItem,
  CategoryConfig,
  HotTopic,
  CategoryType,
} from "../types/explore";

// 分类配置
export const CATEGORIES: Record<CategoryType, CategoryConfig> = {
  tcm: {
    name: "中医理论",
    icon: "leaf",
    color: "#34C759",
    description: "传统中医理论与现代应用",
  },
  nutrition: {
    name: "食疗养生",
    icon: "food-apple",
    color: "#FF9500",
    description: "药食同源，食疗养生",
  },
  exercise: {
    name: "运动养生",
    icon: "run",
    color: "#007AFF",
    description: "太极、八段锦等传统运动",
  },
  mental: {
    name: "心神调养",
    icon: "brain",
    color: "#FF2D92",
    description: "情志调节与心神安宁",
  },
  lifestyle: {
    name: "起居养生",
    icon: "home-heart",
    color: "#5856D6",
    description: "顺应自然的生活方式",
  },
  herbs: {
    name: "本草药材",
    icon: "flower",
    color: "#8E44AD",
    description: "中药材识别与应用",
  },
  acupoints: {
    name: "经络穴位",
    icon: "human-handsup",
    color: "#E74C3C",
    description: "经络穴位与按摩保健",
  },
};

// 老克的智慧内容
export const LAOKE_WISDOM: ContentItem[] = [
  {
    id: "wisdom_1",
    title: "春养肝，夏养心，秋养肺，冬养肾",
    subtitle: "四季养生的根本法则",
    type: "wisdom",
    category: "tcm",
    author: "老克",
    readTime: "8分钟",
    likes: 456,
    image: "🌸",
    tags: ["四季养生", "脏腑调养", "中医理论"],
    difficulty: "beginner",
    featured: true,
    description:
      "中医认为，人体应顺应四季变化调养脏腑，春季重在养肝疏泄，夏季注重养心安神，秋季着重养肺润燥，冬季专注养肾藏精。",
  },
  {
    id: "wisdom_2",
    title: "药食同源话山药",
    subtitle: "山药的药用价值与食疗方法",
    type: "article",
    category: "herbs",
    author: "老克",
    readTime: "6分钟",
    likes: 234,
    image: "🍠",
    tags: ["山药", "药食同源", "脾胃调养"],
    difficulty: "intermediate",
    description:
      "山药性平味甘，归脾、肺、肾经，具有补脾养胃、生津益肺、补肾涩精的功效。",
  },
  {
    id: "wisdom_3",
    title: "太极拳入门心法",
    subtitle: "以意导气，以气运身",
    type: "video",
    category: "exercise",
    author: "老克",
    readTime: "25分钟",
    likes: 789,
    image: "🥋",
    tags: ["太极拳", "气功", "养生运动"],
    difficulty: "beginner",
    featured: true,
    description:
      "太极拳是中华武术的瑰宝，以柔克刚，以静制动，通过缓慢连贯的动作调和气血。",
  },
  {
    id: "wisdom_4",
    title: "足三里穴的妙用",
    subtitle: "常按足三里，胜吃老母鸡",
    type: "course",
    category: "acupoints",
    author: "老克",
    readTime: "12分钟",
    likes: 567,
    image: "🦵",
    tags: ["足三里", "穴位按摩", "保健养生"],
    difficulty: "beginner",
    description:
      "足三里是足阳明胃经的重要穴位，位于小腿外侧，具有调理脾胃、增强体质的作用。",
  },
  {
    id: "wisdom_5",
    title: "五行学说与体质调养",
    subtitle: "根据五行体质制定养生方案",
    type: "theory",
    category: "tcm",
    author: "老克",
    readTime: "15分钟",
    likes: 345,
    image: "☯️",
    tags: ["五行学说", "体质辨识", "个性化养生"],
    difficulty: "advanced",
    description:
      "五行学说是中医理论的重要组成部分，通过木、火、土、金、水五行相生相克关系指导养生。",
  },
  {
    id: "wisdom_6",
    title: "枸杞菊花茶的养生秘密",
    subtitle: "明目养肝的经典搭配",
    type: "recipe",
    category: "nutrition",
    author: "老克",
    readTime: "4分钟",
    likes: 123,
    image: "🍵",
    tags: ["枸杞", "菊花", "明目养肝"],
    difficulty: "beginner",
    description: "枸杞子滋补肝肾，菊花清热明目，两者搭配是养肝明目的经典组合。",
  },
];

// 热门话题
export const HOT_TOPICS: HotTopic[] = [
  { id: "1", title: "春季养肝", count: 1234, icon: "🌱", trending: true },
  { id: "2", title: "中医体质", count: 987, icon: "⚖️" },
  { id: "3", title: "食疗养生", count: 756, icon: "🥗", trending: true },
  { id: "4", title: "穴位按摩", count: 654, icon: "👋" },
  { id: "5", title: "太极养生", count: 543, icon: "🥋" },
  { id: "6", title: "本草识别", count: 432, icon: "🌿" },
];

// 推荐搜索关键词
export const RECOMMENDED_SEARCHES = [
  "春季养生",
  "中医体质",
  "食疗方",
  "穴位按摩",
  "太极拳",
  "八段锦",
  "五行养生",
  "药食同源",
  "经络调理",
  "情志养生",
];

// 内容类型配置
export const CONTENT_TYPE_CONFIG = {
  article: { name: "文章", icon: "file-document", color: "#007AFF" },
  video: { name: "视频", icon: "play-circle", color: "#FF2D92" },
  course: { name: "课程", icon: "school", color: "#34C759" },
  recipe: { name: "食谱", icon: "chef-hat", color: "#FF9500" },
  wisdom: { name: "智慧", icon: "lightbulb", color: "#8E44AD" },
  theory: { name: "理论", icon: "book-open", color: "#5856D6" },
};

// 难度等级配置
export const DIFFICULTY_CONFIG = {
  beginner: { name: "入门", color: "#34C759", description: "适合初学者" },
  intermediate: { name: "进阶", color: "#FF9500", description: "需要一定基础" },
  advanced: { name: "高级", color: "#FF2D92", description: "需要深厚功底" },
};
