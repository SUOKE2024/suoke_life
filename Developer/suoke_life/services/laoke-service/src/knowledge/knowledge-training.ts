/**
 * 知识培训服务
 * 负责课程管理、培训资源和考核认证
 */
import { logger } from '../utils/logger';

/**
 * 课程难度
 */
export enum CourseLevel {
  BEGINNER = 'beginner',       // 入门
  INTERMEDIATE = 'intermediate', // 中级
  ADVANCED = 'advanced',       // 高级
  EXPERT = 'expert'            // 专家
}

/**
 * 课程
 */
export interface Course {
  id: string;                // 课程ID
  title: string;             // 课程标题
  description: string;       // 课程描述
  coverImage?: string;       // 封面图片
  categoryId: string;        // 分类ID
  categoryName: string;      // 分类名称
  level: CourseLevel;        // 课程难度
  duration: number;          // 课程时长(分钟)
  chapterCount: number;      // 章节数量
  authorId: string;          // 作者ID
  authorName: string;        // 作者名称
  enrollCount: number;       // 报名人数
  completionCount: number;   // 完成人数
  rating: number;            // 评分(1-5)
  ratingCount: number;       // 评分人数
  tags?: string[];           // 标签
  price: number;             // 价格
  isFree: boolean;           // 是否免费
  certificate?: boolean;     // 是否有证书
  createdAt: Date;           // 创建时间
  updatedAt: Date;           // 更新时间
  publishedAt?: Date;        // 发布时间
  status: 'draft' | 'published' | 'archived'; // 状态
}

/**
 * 课程章节
 */
export interface Chapter {
  id: string;                // 章节ID
  courseId: string;          // 课程ID
  title: string;             // 章节标题
  description?: string;      // 章节描述
  order: number;             // 排序
  duration: number;          // 章节时长(分钟)
  contentType: 'video' | 'audio' | 'text' | 'quiz'; // 内容类型
  content: string;           // 内容
  mediaUrl?: string;         // 媒体URL
  resourceUrls?: string[];   // 资源URL
  createdAt: Date;           // 创建时间
  updatedAt: Date;           // 更新时间
}

/**
 * 学习记录
 */
export interface LearningRecord {
  id: string;                // 记录ID
  userId: string;            // 用户ID
  courseId: string;          // 课程ID
  chapterIds: string[];      // 已完成章节ID
  progress: number;          // 进度(0-100)
  startedAt: Date;           // 开始时间
  lastAccessAt: Date;        // 最后访问时间
  completedAt?: Date;        // 完成时间
  certificateId?: string;    // 证书ID
  quizScores?: Record<string, number>; // 测验分数
}

/**
 * 证书
 */
export interface Certificate {
  id: string;                // 证书ID
  userId: string;            // 用户ID
  userName: string;          // 用户名称
  courseId: string;          // 课程ID
  courseTitle: string;       // 课程标题
  issuedAt: Date;            // 颁发时间
  expiresAt?: Date;          // 过期时间
  verificationCode: string;  // 验证码
  status: 'active' | 'expired' | 'revoked'; // 状态
}

class KnowledgeTrainingService {
  // 模拟数据存储
  private coursesStore: Map<string, Course> = new Map();
  private chaptersStore: Map<string, Chapter[]> = new Map();
  private learningRecordsStore: Map<string, LearningRecord[]> = new Map();
  private certificatesStore: Map<string, Certificate[]> = new Map();
  
  /**
   * 构造函数
   */
  constructor() {
    logger.info('知识培训服务初始化');
    
    // 初始化示例课程
    this.initSampleCourses();
  }
  
  /**
   * 初始化示例课程
   */
  private initSampleCourses(): void {
    const now = new Date();
    
    // 示例课程1：中医基础入门
    const course1: Course = {
      id: 'course-tcm-basic',
      title: '中医基础入门',
      description: '本课程介绍中医基础理论，包括阴阳五行、脏腑经络等基本概念，适合初学者。',
      coverImage: 'https://placeholder.com/800x450?text=中医基础入门',
      categoryId: 'category-tcm-theory',
      categoryName: '中医理论',
      level: CourseLevel.BEGINNER,
      duration: 180,
      chapterCount: 5,
      authorId: 'laoke',
      authorName: '老克',
      enrollCount: 325,
      completionCount: 156,
      rating: 4.7,
      ratingCount: 87,
      tags: ['中医基础', '入门课程', '阴阳五行'],
      price: 0,
      isFree: true,
      certificate: false,
      createdAt: now,
      updatedAt: now,
      publishedAt: now,
      status: 'published'
    };
    
    // 示例课程2：九种体质辨识与调理
    const course2: Course = {
      id: 'course-constitution',
      title: '九种体质辨识与调理',
      description: '本课程详细介绍中医九种体质的特点、辨识方法和个性化调理方案，帮助学员认识自身体质并进行合理调养。',
      coverImage: 'https://placeholder.com/800x450?text=九种体质辨识与调理',
      categoryId: 'category-constitution',
      categoryName: '体质辨识',
      level: CourseLevel.INTERMEDIATE,
      duration: 240,
      chapterCount: 10,
      authorId: 'laoke',
      authorName: '老克',
      enrollCount: 198,
      completionCount: 85,
      rating: 4.9,
      ratingCount: 56,
      tags: ['体质辨识', '健康调理', '个性化养生'],
      price: 99,
      isFree: false,
      certificate: true,
      createdAt: now,
      updatedAt: now,
      publishedAt: now,
      status: 'published'
    };
    
    // 保存示例课程
    this.coursesStore.set(course1.id, course1);
    this.coursesStore.set(course2.id, course2);
    
    // 创建示例章节
    this.createSampleChapters(course1.id, 5);
    this.createSampleChapters(course2.id, 10);
    
    logger.info('示例课程初始化完成');
  }
  
  /**
   * 创建示例章节
   * @param courseId 课程ID
   * @param count 章节数量
   */
  private createSampleChapters(courseId: string, count: number): void {
    const now = new Date();
    const chapters: Chapter[] = [];
    
    const contentTypes: ('video' | 'audio' | 'text' | 'quiz')[] = ['video', 'text', 'quiz'];
    
    for (let i = 1; i <= count; i++) {
      const course = this.coursesStore.get(courseId)!;
      const contentType = contentTypes[i % contentTypes.length];
      
      chapters.push({
        id: `chapter-${courseId}-${i}`,
        courseId,
        title: `第${i}章：${course.title}基础知识(${i})`,
        description: `本章介绍${course.title}的基础知识第${i}部分，包含理论讲解和实际案例。`,
        order: i,
        duration: 15 + (i * 5),
        contentType,
        content: `本章详细内容将根据学习进度显示，包括${contentType}内容和练习。`,
        mediaUrl: contentType === 'video' || contentType === 'audio'
          ? `https://example.com/media/${courseId}-chapter-${i}.mp4`
          : undefined,
        resourceUrls: [
          `https://example.com/resources/${courseId}-chapter-${i}-slides.pdf`,
          `https://example.com/resources/${courseId}-chapter-${i}-notes.pdf`
        ],
        createdAt: now,
        updatedAt: now
      });
    }
    
    this.chaptersStore.set(courseId, chapters);
  }
  
  /**
   * 获取课程列表
   * @param categoryId 分类ID
   * @param level 课程难度
   * @param page 页码
   * @param limit 每页数量
   * @returns 课程列表和分页信息
   */
  public async getCourses(
    categoryId?: string,
    level?: string,
    page: number = 1,
    limit: number = 10
  ): Promise<{
    courses: Course[];
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  }> {
    // 获取所有已发布的课程
    let courses = Array.from(this.coursesStore.values())
      .filter(course => course.status === 'published');
    
    // 分类过滤
    if (categoryId) {
      courses = courses.filter(course => course.categoryId === categoryId);
    }
    
    // 难度过滤
    if (level) {
      courses = courses.filter(course => course.level === level);
    }
    
    // 计算分页信息
    const total = courses.length;
    const totalPages = Math.ceil(total / limit);
    const offset = (page - 1) * limit;
    
    // 按报名人数排序
    courses.sort((a, b) => b.enrollCount - a.enrollCount);
    
    // 分页
    const paginatedCourses = courses.slice(offset, offset + limit);
    
    logger.info(`获取课程列表`, {
      categoryId,
      level,
      page,
      limit,
      total
    });
    
    return {
      courses: paginatedCourses,
      total,
      page,
      limit,
      totalPages
    };
  }
  
  /**
   * 获取课程详情
   * @param id 课程ID
   * @returns 课程详情
   */
  public async getCourseById(id: string): Promise<Course | null> {
    if (!this.coursesStore.has(id)) {
      logger.warn(`获取失败，课程不存在: ${id}`);
      return null;
    }
    
    const course = this.coursesStore.get(id)!;
    
    logger.info(`获取课程详情`, {
      id,
      title: course.title
    });
    
    return course;
  }
  
  /**
   * 获取课程章节
   * @param courseId 课程ID
   * @returns 章节列表
   */
  public async getCourseChapters(courseId: string): Promise<Chapter[]> {
    if (!this.coursesStore.has(courseId)) {
      logger.warn(`获取失败，课程不存在: ${courseId}`);
      return [];
    }
    
    if (!this.chaptersStore.has(courseId)) {
      logger.warn(`课程没有章节: ${courseId}`);
      return [];
    }
    
    const chapters = this.chaptersStore.get(courseId)!;
    
    // 按顺序排序
    chapters.sort((a, b) => a.order - b.order);
    
    logger.info(`获取课程章节`, {
      courseId,
      count: chapters.length
    });
    
    return chapters;
  }
  
  /**
   * 用户报名课程
   * @param userId 用户ID
   * @param courseId 课程ID
   * @returns 是否报名成功
   */
  public async enrollCourse(
    userId: string,
    courseId: string
  ): Promise<boolean> {
    if (!this.coursesStore.has(courseId)) {
      logger.warn(`报名失败，课程不存在: ${courseId}`);
      return false;
    }
    
    // 检查用户是否已报名
    if (this.learningRecordsStore.has(userId)) {
      const userRecords = this.learningRecordsStore.get(userId)!;
      const existingRecord = userRecords.find(record => record.courseId === courseId);
      
      if (existingRecord) {
        logger.warn(`用户已报名课程: ${courseId}`, { userId });
        return true;
      }
    }
    
    // 获取课程信息
    const course = this.coursesStore.get(courseId)!;
    
    // 创建学习记录
    const now = new Date();
    const learningRecord: LearningRecord = {
      id: `record-${userId}-${courseId}`,
      userId,
      courseId,
      chapterIds: [],
      progress: 0,
      startedAt: now,
      lastAccessAt: now
    };
    
    // 保存学习记录
    if (!this.learningRecordsStore.has(userId)) {
      this.learningRecordsStore.set(userId, []);
    }
    
    this.learningRecordsStore.get(userId)!.push(learningRecord);
    
    // 更新课程报名人数
    course.enrollCount += 1;
    this.coursesStore.set(courseId, course);
    
    logger.info(`用户报名课程`, {
      userId,
      courseId,
      courseName: course.title
    });
    
    return true;
  }
  
  /**
   * 更新学习进度
   * @param userId 用户ID
   * @param courseId 课程ID
   * @param chapterId 章节ID
   * @param completed 是否完成
   * @returns 更新后的学习记录
   */
  public async updateLearningProgress(
    userId: string,
    courseId: string,
    chapterId: string,
    completed: boolean
  ): Promise<LearningRecord | null> {
    // 检查用户是否已报名
    if (!this.learningRecordsStore.has(userId)) {
      logger.warn(`更新失败，用户未报名任何课程: ${userId}`);
      return null;
    }
    
    const userRecords = this.learningRecordsStore.get(userId)!;
    const recordIndex = userRecords.findIndex(record => record.courseId === courseId);
    
    if (recordIndex === -1) {
      logger.warn(`更新失败，用户未报名该课程: ${courseId}`, { userId });
      return null;
    }
    
    // 获取学习记录
    const record = userRecords[recordIndex];
    
    // 获取课程章节
    if (!this.chaptersStore.has(courseId)) {
      logger.warn(`更新失败，课程没有章节: ${courseId}`);
      return null;
    }
    
    const chapters = this.chaptersStore.get(courseId)!;
    
    // 检查章节是否存在
    const chapterExists = chapters.some(chapter => chapter.id === chapterId);
    if (!chapterExists) {
      logger.warn(`更新失败，章节不存在: ${chapterId}`);
      return null;
    }
    
    // 更新完成的章节
    if (completed) {
      if (!record.chapterIds.includes(chapterId)) {
        record.chapterIds.push(chapterId);
      }
    } else {
      const index = record.chapterIds.indexOf(chapterId);
      if (index !== -1) {
        record.chapterIds.splice(index, 1);
      }
    }
    
    // 计算进度
    record.progress = Math.round((record.chapterIds.length / chapters.length) * 100);
    record.lastAccessAt = new Date();
    
    // 检查是否完成全部章节
    if (record.progress === 100 && !record.completedAt) {
      record.completedAt = new Date();
      
      // 更新课程完成人数
      const course = this.coursesStore.get(courseId)!;
      course.completionCount += 1;
      this.coursesStore.set(courseId, course);
      
      // 如果课程有证书，颁发证书
      if (course.certificate) {
        await this.issueCertificate(userId, 'Unknown User', courseId);
      }
    }
    
    // 保存更新
    userRecords[recordIndex] = record;
    this.learningRecordsStore.set(userId, userRecords);
    
    logger.info(`更新学习进度`, {
      userId,
      courseId,
      chapterId,
      completed,
      newProgress: record.progress
    });
    
    return record;
  }
  
  /**
   * 颁发证书
   * @param userId 用户ID
   * @param userName 用户名称
   * @param courseId 课程ID
   * @returns 证书ID
   */
  private async issueCertificate(
    userId: string,
    userName: string,
    courseId: string
  ): Promise<string> {
    if (!this.coursesStore.has(courseId)) {
      throw new Error(`课程不存在: ${courseId}`);
    }
    
    const course = this.coursesStore.get(courseId)!;
    
    // 生成验证码
    const verificationCode = `CERT-${Date.now().toString(36)}-${Math.random().toString(36).substring(2, 8)}`.toUpperCase();
    
    // 创建证书
    const now = new Date();
    const certificate: Certificate = {
      id: `cert-${userId}-${courseId}`,
      userId,
      userName,
      courseId,
      courseTitle: course.title,
      issuedAt: now,
      verificationCode,
      status: 'active'
    };
    
    // 保存证书
    if (!this.certificatesStore.has(userId)) {
      this.certificatesStore.set(userId, []);
    }
    
    this.certificatesStore.get(userId)!.push(certificate);
    
    logger.info(`颁发证书`, {
      userId,
      userName,
      courseId,
      courseTitle: course.title,
      certificateId: certificate.id
    });
    
    return certificate.id;
  }
  
  /**
   * 获取用户学习记录
   * @param userId 用户ID
   * @returns 学习记录列表
   */
  public async getUserLearningRecords(userId: string): Promise<{
    record: LearningRecord;
    course: Course;
  }[]> {
    if (!this.learningRecordsStore.has(userId)) {
      return [];
    }
    
    const userRecords = this.learningRecordsStore.get(userId)!;
    
    // 获取课程详情
    const result = userRecords.map(record => {
      const course = this.coursesStore.get(record.courseId) || {
        id: record.courseId,
        title: '未知课程',
        description: '',
        categoryId: '',
        categoryName: '',
        level: CourseLevel.BEGINNER,
        duration: 0,
        chapterCount: 0,
        authorId: '',
        authorName: '',
        enrollCount: 0,
        completionCount: 0,
        rating: 0,
        ratingCount: 0,
        price: 0,
        isFree: true,
        createdAt: new Date(),
        updatedAt: new Date(),
        status: 'archived'
      };
      
      return {
        record,
        course
      };
    });
    
    // 按最后访问时间排序
    result.sort((a, b) => b.record.lastAccessAt.getTime() - a.record.lastAccessAt.getTime());
    
    logger.info(`获取用户学习记录`, {
      userId,
      count: result.length
    });
    
    return result;
  }
  
  /**
   * 获取用户证书
   * @param userId 用户ID
   * @returns 证书列表
   */
  public async getUserCertificates(userId: string): Promise<Certificate[]> {
    if (!this.certificatesStore.has(userId)) {
      return [];
    }
    
    const certificates = this.certificatesStore.get(userId)!;
    
    // 按颁发时间排序
    certificates.sort((a, b) => b.issuedAt.getTime() - a.issuedAt.getTime());
    
    logger.info(`获取用户证书`, {
      userId,
      count: certificates.length
    });
    
    return certificates;
  }
  
  /**
   * 验证证书
   * @param verificationCode 验证码
   * @returns 证书信息或null
   */
  public async verifyCertificate(
    verificationCode: string
  ): Promise<Certificate | null> {
    // 遍历所有用户的证书
    for (const [userId, certificates] of this.certificatesStore.entries()) {
      const certificate = certificates.find(
        cert => cert.verificationCode === verificationCode
      );
      
      if (certificate) {
        logger.info(`验证证书`, {
          verificationCode,
          userId,
          courseId: certificate.courseId
        });
        
        return certificate;
      }
    }
    
    logger.warn(`证书验证失败，验证码无效: ${verificationCode}`);
    return null;
  }
}

// 导出单例实例
const knowledgeTrainingService = new KnowledgeTrainingService();
export default knowledgeTrainingService;