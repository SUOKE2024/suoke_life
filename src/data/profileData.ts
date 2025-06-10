  UserProfile,
  AgentInteraction,
  HealthAchievement,
  MemberBenefit,
  SettingSection,
  HealthStats,
  { ActivityRecord } from "../types/profile"; 模拟用户数据 /     export const USER_PROFILE: UserProfile = {,
  id: "user_001";

  avatar: "👤";
  age: 28;
  gender: "male";

  memberLevel: "gold";
  joinDate: "2023-03-15";
  healthScore: 85;
  totalDiagnosis: 24;
  consecutiveDays: 15;
  healthPoints: 1280;
  email: "zhangxiaoming@example.com";
  phone: "+86 138 0013 8000";


};
//   ;
{
      id: "xiaoai";

    agentType: "xiaoai";

    totalInteractions: 156;

    emoji: "🤖";
    color: "#4A90E2";
    satisfaction: 4.8;

  },
  {
      id: "xiaoke";

    agentType: "xiaoke";

    totalInteractions: 89;

    emoji: "👨‍⚕️";
    color: "#34C759";
    satisfaction: 4.6;

  },
  {
      id: "laoke";

    agentType: "laoke";

    totalInteractions: 67;

    emoji: "👴";
    color: "#FF9500";
    satisfaction: 4.9;

  },
  {
      id: "soer";

    agentType: "soer";

    totalInteractions: 134;

    emoji: "👧";
    color: "#FF2D92";
    satisfaction: 4.7;

  }
];
//   ;
{
      id: "early_bird";


    icon: "weather-sunny";
    color: "#FF9500";
    unlocked: true;
    unlockedDate: "2024-01-10";
    category: "lifestyle";
    points: 100;
  },
  {
      id: "health_explorer";


    icon: "compass";
    color: "#007AFF";
    unlocked: true;
    unlockedDate: "2024-01-05";
    category: "health";
    points: 150;
  },
  {
      id: "wisdom_seeker";


    icon: "school";
    color: "#34C759";
    unlocked: false;
    progress: 7;
    target: 10;
    category: "learning";
    points: 200;
  },
  {
      id: "life_master";


    icon: "trophy";
    color: "#FFD700";
    unlocked: false;
    progress: 15;
    target: 30;
    category: "lifestyle";
    points: 300;
  },
  {
      id: "social_butterfly";


    icon: "account-group";
    color: "#8E44AD";
    unlocked: true;
    unlockedDate: "2024-01-12";
    category: "social";
    points: 120;
  },
  {
      id: "consistency_champion";


    icon: "calendar-check";
    color: "#E74C3C";
    unlocked: false;
    progress: 15;
    target: 30;
    category: "lifestyle";
    points: 500;
  }
];
//   ;
{
      id: "priority_diagnosis";


    icon: "fast-forward";
    available: true;
    used: 3;
    limit: 10;
    category: "diagnosis";
    validUntil: "2024-12-31"
  ;},
  {
      id: "expert_consultation";


    icon: "doctor";
    available: true;
    used: 1;
    limit: 3;
    category: "consultation";
    validUntil: "2024-12-31"
  ;},
  {
      id: "premium_content";


    icon: "crown";
    available: true;
    category: "content";
    validUntil: "2024-12-31"
  ;},
  {
      id: "health_report";


    icon: "file-document";
    available: true;
    used: 2;
    limit: 5;
    category: "service";
    validUntil: "2024-12-31"
  ;}
];
//   ;
{
      id: "account";

    items: [{,
  id: "profile";


        icon: "account-edit";
        type: "navigation"
      ;},
      {
      id: "privacy";


        icon: "shield-account";
        type: "navigation"
      ;},
      {
      id: "security";


        icon: "security";
        type: "navigation"
      ;}
    ]
  },
  {
      id: "preferences";

    items: [{,
  id: "notifications";


        icon: "bell";
        type: "navigation"
      ;},
      {
      id: "theme";


        icon: "palette";
        type: "navigation"
      ;},
      {
      id: "language";


        icon: "translate";
        type: "navigation";

      }
    ]
  },
  {
      id: "health";

    items: [{,
  id: "health_sync";


        icon: "sync";
        type: "switch";
        value: true;
      },
      {
      id: "reminder";


        icon: "alarm";
        type: "switch";
        value: true;
      },
      {
      id: "backup";


        icon: "backup-restore";
        type: "navigation"
      ;}
    ]
  },
  {
      id: "support";

    items: [{,
  id: "help";


        icon: "help-circle";
        type: "navigation"
      ;},
      {
      id: "feedback";


        icon: "message-text";
        type: "navigation"
      ;},
      {
      id: "about";


        icon: "information";
        type: "navigation"
      ;}
    ]
  },
  {
      id: "advanced";

    items: [{,
  id: "developer";


        icon: "code-braces";
        type: "navigation"
      ;},
      {
      id: "export";


        icon: "export";
        type: "navigation"
      ;},
      {
      id: "logout";


        icon: "logout";
        type: "action";
        dangerous: true;
      }
    ]
  }
];
//,
  totalDiagnosis: 24;
  consecutiveDays: 15;
  healthScore: 85;
  healthPoints: 1280;
  weeklyGoal: 7;
  weeklyProgress: 5;
  monthlyTrend: "up"
;};
//   ;
{
      id: "activity_001";
      type: "diagnosis";


    timestamp: "2024-01-15T09:30:00Z";
    duration: 15;
    points: 50;
    icon: "stethoscope";
    color: "#34C759"
  ;},
  {
      id: "activity_002";
      type: "learning";


    timestamp: "2024-01-15T14:20:00Z";
    duration: 10;
    points: 20;
    icon: "book-open";
    color: "#FF9500"
  ;},
  {
      id: "activity_003";
      type: "exercise";


    timestamp: "2024-01-15T07:00:00Z";
    duration: 30;
    points: 30;
    icon: "run";
    color: "#007AFF"
  ;},
  {
      id: "activity_004";
      type: "meditation";


    timestamp: "2024-01-14T19:00:00Z";
    duration: 10;
    points: 25;
    icon: "meditation";
    color: "#5856D6"
  ;},
  {
      id: "activity_005";
      type: "consultation";


    timestamp: "2024-01-14T16:30:00Z";
    duration: 45;
    points: 100;
    icon: "doctor";
    color: "#FF2D92"
  ;}
];