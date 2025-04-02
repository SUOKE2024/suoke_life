import mongoose, { Document, Schema } from 'mongoose';

/**
 * 培训课程类型枚举
 */
export enum CourseType {
  VIDEO = 'video',
  INTERACTIVE = 'interactive',
  DOCUMENT = 'document',
  LIVE = 'live',
  MIXED = 'mixed'
}

/**
 * 培训难度级别枚举
 */
export enum DifficultyLevel {
  BEGINNER = 'beginner',
  INTERMEDIATE = 'intermediate',
  ADVANCED = 'advanced',
  EXPERT = 'expert'
}

/**
 * 课程章节状态枚举
 */
export enum ChapterStatus {
  NOT_STARTED = 'not_started',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed'
}

/**
 * 课程注册状态枚举
 */
export enum EnrollmentStatus {
  ACTIVE = 'active',
  COMPLETED = 'completed',
  DROPPED = 'dropped',
  SUSPENDED = 'suspended'
}

/**
 * 课程章节接口
 */
export interface IChapter extends Document {
  title: string;
  description: string;
  order: number;
  duration: number; // 分钟
  contentUrl: string;
  thumbnailUrl?: string;
  resources?: {
    title: string;
    description?: string;
    url: string;
    type: string;
  }[];
  quiz?: {
    questions: {
      text: string;
      options: string[];
      correctOption: number;
    }[];
    passingScore: number;
  };
}

/**
 * 培训课程接口
 */
export interface ICourse extends Document {
  title: string;
  description: string;
  summary: string;
  courseType: CourseType;
  difficultyLevel: DifficultyLevel;
  thumbnailUrl: string;
  coverImageUrl?: string;
  duration: number; // 总时长（分钟）
  instructor: {
    name: string;
    bio?: string;
    avatarUrl?: string;
  };
  tags: string[];
  prerequisites?: string[];
  chapters: IChapter[];
  isActive: boolean;
  isPublic: boolean;
  enrollmentCount: number;
  avgRating: number;
  reviewCount: number;
  price?: number;
  createdAt: Date;
  updatedAt: Date;
}

/**
 * 进度跟踪接口
 */
export interface IProgress extends Document {
  userId: mongoose.Types.ObjectId;
  courseId: mongoose.Types.ObjectId;
  chapterId: mongoose.Types.ObjectId;
  status: ChapterStatus;
  startedAt: Date;
  completedAt?: Date;
  lastAccessedAt: Date;
  timeSpent: number; // 花费时间（秒）
  quizScore?: number; // 测验得分
  notes?: string;
}

/**
 * 课程注册接口
 */
export interface IEnrollment extends Document {
  userId: mongoose.Types.ObjectId;
  courseId: mongoose.Types.ObjectId;
  status: EnrollmentStatus;
  enrolledAt: Date;
  completedAt?: Date;
  lastAccessedAt: Date;
  progress: {
    completedChapters: number;
    totalChapters: number;
    percentageCompleted: number;
  };
  certificate?: {
    issued: boolean;
    issuedAt?: Date;
    certificateUrl?: string;
  };
  paymentInfo?: {
    paid: boolean;
    amount: number;
    transactionId?: string;
    paymentDate?: Date;
  };
}

/**
 * 课程评价接口
 */
export interface IReview extends Document {
  userId: mongoose.Types.ObjectId;
  courseId: mongoose.Types.ObjectId;
  rating: number; // 1-5
  comment?: string;
  createdAt: Date;
  updatedAt: Date;
}

/**
 * 章节Schema
 */
const ChapterSchema = new Schema<IChapter>({
  title: {
    type: String,
    required: true,
    trim: true
  },
  description: {
    type: String,
    required: true
  },
  order: {
    type: Number,
    required: true
  },
  duration: {
    type: Number,
    required: true
  },
  contentUrl: {
    type: String,
    required: true
  },
  thumbnailUrl: {
    type: String
  },
  resources: [
    {
      title: {
        type: String,
        required: true
      },
      description: {
        type: String
      },
      url: {
        type: String,
        required: true
      },
      type: {
        type: String,
        required: true
      }
    }
  ],
  quiz: {
    questions: [
      {
        text: {
          type: String,
          required: true
        },
        options: {
          type: [String],
          required: true
        },
        correctOption: {
          type: Number,
          required: true
        }
      }
    ],
    passingScore: {
      type: Number,
      required: true,
      default: 70
    }
  }
});

/**
 * 课程Schema
 */
const CourseSchema = new Schema<ICourse>(
  {
    title: {
      type: String,
      required: true,
      trim: true,
      index: true
    },
    description: {
      type: String,
      required: true
    },
    summary: {
      type: String,
      required: true
    },
    courseType: {
      type: String,
      enum: Object.values(CourseType),
      required: true,
      index: true
    },
    difficultyLevel: {
      type: String,
      enum: Object.values(DifficultyLevel),
      required: true,
      index: true
    },
    thumbnailUrl: {
      type: String,
      required: true
    },
    coverImageUrl: {
      type: String
    },
    duration: {
      type: Number,
      required: true
    },
    instructor: {
      name: {
        type: String,
        required: true
      },
      bio: {
        type: String
      },
      avatarUrl: {
        type: String
      }
    },
    tags: {
      type: [String],
      index: true
    },
    prerequisites: {
      type: [String]
    },
    chapters: [ChapterSchema],
    isActive: {
      type: Boolean,
      default: true,
      index: true
    },
    isPublic: {
      type: Boolean,
      default: true,
      index: true
    },
    enrollmentCount: {
      type: Number,
      default: 0
    },
    avgRating: {
      type: Number,
      default: 0
    },
    reviewCount: {
      type: Number,
      default: 0
    },
    price: {
      type: Number
    }
  },
  {
    timestamps: true
  }
);

/**
 * 进度Schema
 */
const ProgressSchema = new Schema<IProgress>(
  {
    userId: {
      type: Schema.Types.ObjectId,
      ref: 'User',
      required: true,
      index: true
    },
    courseId: {
      type: Schema.Types.ObjectId,
      ref: 'Course',
      required: true,
      index: true
    },
    chapterId: {
      type: Schema.Types.ObjectId,
      required: true
    },
    status: {
      type: String,
      enum: Object.values(ChapterStatus),
      default: ChapterStatus.NOT_STARTED,
      index: true
    },
    startedAt: {
      type: Date,
      default: Date.now
    },
    completedAt: {
      type: Date
    },
    lastAccessedAt: {
      type: Date,
      default: Date.now
    },
    timeSpent: {
      type: Number,
      default: 0
    },
    quizScore: {
      type: Number
    },
    notes: {
      type: String
    }
  },
  {
    timestamps: true
  }
);

/**
 * 注册Schema
 */
const EnrollmentSchema = new Schema<IEnrollment>(
  {
    userId: {
      type: Schema.Types.ObjectId,
      ref: 'User',
      required: true,
      index: true
    },
    courseId: {
      type: Schema.Types.ObjectId,
      ref: 'Course',
      required: true,
      index: true
    },
    status: {
      type: String,
      enum: Object.values(EnrollmentStatus),
      default: EnrollmentStatus.ACTIVE,
      index: true
    },
    enrolledAt: {
      type: Date,
      default: Date.now
    },
    completedAt: {
      type: Date
    },
    lastAccessedAt: {
      type: Date,
      default: Date.now
    },
    progress: {
      completedChapters: {
        type: Number,
        default: 0
      },
      totalChapters: {
        type: Number,
        required: true
      },
      percentageCompleted: {
        type: Number,
        default: 0
      }
    },
    certificate: {
      issued: {
        type: Boolean,
        default: false
      },
      issuedAt: {
        type: Date
      },
      certificateUrl: {
        type: String
      }
    },
    paymentInfo: {
      paid: {
        type: Boolean,
        default: false
      },
      amount: {
        type: Number,
        default: 0
      },
      transactionId: {
        type: String
      },
      paymentDate: {
        type: Date
      }
    }
  },
  {
    timestamps: true
  }
);

/**
 * 评价Schema
 */
const ReviewSchema = new Schema<IReview>(
  {
    userId: {
      type: Schema.Types.ObjectId,
      ref: 'User',
      required: true,
      index: true
    },
    courseId: {
      type: Schema.Types.ObjectId,
      ref: 'Course',
      required: true,
      index: true
    },
    rating: {
      type: Number,
      required: true,
      min: 1,
      max: 5
    },
    comment: {
      type: String
    }
  },
  {
    timestamps: true
  }
);

// 创建复合索引
ProgressSchema.index({ userId: 1, courseId: 1, chapterId: 1 }, { unique: true });
EnrollmentSchema.index({ userId: 1, courseId: 1 }, { unique: true });
ReviewSchema.index({ userId: 1, courseId: 1 }, { unique: true });

// 创建模型
export const CourseModel = mongoose.model<ICourse>('Course', CourseSchema);
export const ProgressModel = mongoose.model<IProgress>('Progress', ProgressSchema);
export const EnrollmentModel = mongoose.model<IEnrollment>('Enrollment', EnrollmentSchema);
export const ReviewModel = mongoose.model<IReview>('Review', ReviewSchema); 