import mongoose from 'mongoose';
import { 
  CourseModel, 
  ICourse, 
  ProgressModel, 
  IProgress, 
  EnrollmentModel, 
  IEnrollment, 
  ReviewModel, 
  IReview,
  ChapterStatus,
  EnrollmentStatus
} from '../../models/training.model';
import logger from '../../core/utils/logger';
import { ApiError } from '../../core/utils/errors';

/**
 * 获取所有课程
 */
export const getAllCourses = async (
  query: Record<string, any> = {},
  limit: number = 20,
  skip: number = 0,
  sort: Record<string, number> = { createdAt: -1 }
): Promise<{ total: number; courses: ICourse[] }> => {
  try {
    // 默认只获取激活的课程
    const filters = { isActive: true, ...query };
    
    const total = await CourseModel.countDocuments(filters);
    const courses = await CourseModel.find(filters)
      .sort(sort)
      .skip(skip)
      .limit(limit);
    
    return { total, courses };
  } catch (error) {
    logger.error('获取课程列表失败:', error);
    throw error;
  }
};

/**
 * 根据ID获取课程详情
 */
export const getCourseById = async (courseId: string): Promise<ICourse> => {
  try {
    const course = await CourseModel.findById(courseId);
    
    if (!course) {
      throw new ApiError(404, `未找到ID为 ${courseId} 的课程`);
    }
    
    return course;
  } catch (error) {
    logger.error(`获取课程详情失败 [ID: ${courseId}]:`, error);
    throw error;
  }
};

/**
 * 搜索课程
 */
export const searchCourses = async (
  searchTerm: string,
  filters: Record<string, any> = {},
  limit: number = 20,
  skip: number = 0
): Promise<{ total: number; courses: ICourse[] }> => {
  try {
    // 构建搜索查询
    const searchQuery = {
      isActive: true,
      $or: [
        { title: { $regex: searchTerm, $options: 'i' } },
        { description: { $regex: searchTerm, $options: 'i' } },
        { summary: { $regex: searchTerm, $options: 'i' } },
        { tags: { $in: [new RegExp(searchTerm, 'i')] } }
      ],
      ...filters
    };
    
    const total = await CourseModel.countDocuments(searchQuery);
    const courses = await CourseModel.find(searchQuery)
      .sort({ avgRating: -1, enrollmentCount: -1 })
      .skip(skip)
      .limit(limit);
    
    return { total, courses };
  } catch (error) {
    logger.error(`搜索课程失败 [关键词: ${searchTerm}]:`, error);
    throw error;
  }
};

/**
 * 创建新课程
 */
export const createCourse = async (courseData: Partial<ICourse>): Promise<ICourse> => {
  try {
    const course = new CourseModel(courseData);
    await course.save();
    return course;
  } catch (error) {
    logger.error('创建课程失败:', error);
    throw error;
  }
};

/**
 * 更新课程信息
 */
export const updateCourse = async (
  courseId: string,
  updateData: Partial<ICourse>
): Promise<ICourse> => {
  try {
    const course = await CourseModel.findByIdAndUpdate(
      courseId,
      { $set: updateData },
      { new: true, runValidators: true }
    );
    
    if (!course) {
      throw new ApiError(404, `未找到ID为 ${courseId} 的课程`);
    }
    
    return course;
  } catch (error) {
    logger.error(`更新课程失败 [ID: ${courseId}]:`, error);
    throw error;
  }
};

/**
 * 删除课程
 */
export const deleteCourse = async (courseId: string): Promise<{ success: boolean }> => {
  try {
    // 检查课程是否存在
    const course = await CourseModel.findById(courseId);
    
    if (!course) {
      throw new ApiError(404, `未找到ID为 ${courseId} 的课程`);
    }
    
    // 检查是否有用户已注册此课程
    const enrollmentCount = await EnrollmentModel.countDocuments({ courseId });
    
    if (enrollmentCount > 0) {
      // 如果有用户注册，则只将课程标记为非活动
      course.isActive = false;
      await course.save();
      
      return { success: true };
    }
    
    // 如果没有用户注册，则可以完全删除
    await CourseModel.findByIdAndDelete(courseId);
    
    // 清理相关数据
    await Promise.all([
      ProgressModel.deleteMany({ courseId }),
      ReviewModel.deleteMany({ courseId })
    ]);
    
    return { success: true };
  } catch (error) {
    logger.error(`删除课程失败 [ID: ${courseId}]:`, error);
    throw error;
  }
};

/**
 * 注册课程
 */
export const enrollCourse = async (
  userId: string,
  courseId: string,
  paymentInfo?: {
    paid: boolean;
    amount: number;
    transactionId?: string;
  }
): Promise<IEnrollment> => {
  try {
    // 检查课程是否存在且处于活动状态
    const course = await CourseModel.findOne({ _id: courseId, isActive: true });
    
    if (!course) {
      throw new ApiError(404, `未找到ID为 ${courseId} 的有效课程`);
    }
    
    // 检查用户是否已注册此课程
    const existingEnrollment = await EnrollmentModel.findOne({
      userId: new mongoose.Types.ObjectId(userId),
      courseId: new mongoose.Types.ObjectId(courseId)
    });
    
    if (existingEnrollment) {
      // 如果用户之前注册过但已退出，可以重新激活
      if (existingEnrollment.status === EnrollmentStatus.DROPPED ||
          existingEnrollment.status === EnrollmentStatus.SUSPENDED) {
        existingEnrollment.status = EnrollmentStatus.ACTIVE;
        existingEnrollment.lastAccessedAt = new Date();
        
        await existingEnrollment.save();
        return existingEnrollment;
      }
      
      throw new ApiError(400, '您已注册此课程');
    }
    
    // 处理付款信息
    let payment = undefined;
    if (course.price && course.price > 0) {
      if (!paymentInfo || !paymentInfo.paid) {
        throw new ApiError(400, '此课程需要付费，请提供有效的付款信息');
      }
      
      payment = {
        paid: paymentInfo.paid,
        amount: paymentInfo.amount,
        transactionId: paymentInfo.transactionId,
        paymentDate: new Date()
      };
    }
    
    // 创建新的注册记录
    const enrollment = new EnrollmentModel({
      userId: new mongoose.Types.ObjectId(userId),
      courseId: new mongoose.Types.ObjectId(courseId),
      status: EnrollmentStatus.ACTIVE,
      enrolledAt: new Date(),
      lastAccessedAt: new Date(),
      progress: {
        completedChapters: 0,
        totalChapters: course.chapters.length,
        percentageCompleted: 0
      },
      paymentInfo: payment
    });
    
    await enrollment.save();
    
    // 更新课程的注册人数
    await CourseModel.findByIdAndUpdate(
      courseId,
      { $inc: { enrollmentCount: 1 } }
    );
    
    return enrollment;
  } catch (error) {
    logger.error(`注册课程失败 [用户ID: ${userId}, 课程ID: ${courseId}]:`, error);
    throw error;
  }
};

/**
 * 获取用户的课程注册列表
 */
export const getUserEnrollments = async (
  userId: string,
  status?: EnrollmentStatus,
  limit: number = 20,
  skip: number = 0
): Promise<{ total: number; enrollments: IEnrollment[] }> => {
  try {
    // 构建查询条件
    const query: Record<string, any> = { 
      userId: new mongoose.Types.ObjectId(userId) 
    };
    
    if (status) {
      query.status = status;
    }
    
    const total = await EnrollmentModel.countDocuments(query);
    const enrollments = await EnrollmentModel.find(query)
      .sort({ lastAccessedAt: -1 })
      .skip(skip)
      .limit(limit)
      .populate('courseId', 'title thumbnailUrl courseType difficultyLevel duration');
    
    return { total, enrollments };
  } catch (error) {
    logger.error(`获取用户课程注册列表失败 [用户ID: ${userId}]:`, error);
    throw error;
  }
};

/**
 * 获取特定课程的注册详情
 */
export const getEnrollmentDetails = async (
  userId: string,
  courseId: string
): Promise<IEnrollment> => {
  try {
    const enrollment = await EnrollmentModel.findOne({
      userId: new mongoose.Types.ObjectId(userId),
      courseId: new mongoose.Types.ObjectId(courseId)
    }).populate('courseId');
    
    if (!enrollment) {
      throw new ApiError(404, '未找到课程注册记录');
    }
    
    return enrollment;
  } catch (error) {
    logger.error(`获取注册详情失败 [用户ID: ${userId}, 课程ID: ${courseId}]:`, error);
    throw error;
  }
};

/**
 * 更新课程注册状态
 */
export const updateEnrollmentStatus = async (
  userId: string,
  courseId: string,
  status: EnrollmentStatus
): Promise<IEnrollment> => {
  try {
    const enrollment = await EnrollmentModel.findOne({
      userId: new mongoose.Types.ObjectId(userId),
      courseId: new mongoose.Types.ObjectId(courseId)
    });
    
    if (!enrollment) {
      throw new ApiError(404, '未找到课程注册记录');
    }
    
    // 更新状态
    enrollment.status = status;
    enrollment.lastAccessedAt = new Date();
    
    // 如果状态是已完成，设置完成时间
    if (status === EnrollmentStatus.COMPLETED && !enrollment.completedAt) {
      enrollment.completedAt = new Date();
    }
    
    await enrollment.save();
    return enrollment;
  } catch (error) {
    logger.error(`更新注册状态失败 [用户ID: ${userId}, 课程ID: ${courseId}]:`, error);
    throw error;
  }
};

/**
 * 更新章节进度
 */
export const updateChapterProgress = async (
  userId: string,
  courseId: string,
  chapterId: string,
  progressData: {
    status: ChapterStatus;
    timeSpent?: number;
    quizScore?: number;
    notes?: string;
  }
): Promise<IProgress> => {
  try {
    // 查找或创建进度记录
    let progress = await ProgressModel.findOne({
      userId: new mongoose.Types.ObjectId(userId),
      courseId: new mongoose.Types.ObjectId(courseId),
      chapterId: new mongoose.Types.ObjectId(chapterId)
    });
    
    const now = new Date();
    
    if (!progress) {
      // 创建新的进度记录
      progress = new ProgressModel({
        userId: new mongoose.Types.ObjectId(userId),
        courseId: new mongoose.Types.ObjectId(courseId),
        chapterId: new mongoose.Types.ObjectId(chapterId),
        status: progressData.status,
        startedAt: now,
        lastAccessedAt: now,
        timeSpent: progressData.timeSpent || 0,
        quizScore: progressData.quizScore,
        notes: progressData.notes
      });
    } else {
      // 更新现有记录
      progress.status = progressData.status;
      progress.lastAccessedAt = now;
      
      if (progressData.timeSpent) {
        progress.timeSpent += progressData.timeSpent;
      }
      
      if (progressData.quizScore !== undefined) {
        progress.quizScore = progressData.quizScore;
      }
      
      if (progressData.notes) {
        progress.notes = progressData.notes;
      }
    }
    
    // 如果章节已完成，设置完成时间
    if (progressData.status === ChapterStatus.COMPLETED && !progress.completedAt) {
      progress.completedAt = now;
      
      // 更新课程注册的整体进度
      await updateEnrollmentProgress(userId, courseId);
    }
    
    await progress.save();
    return progress;
  } catch (error) {
    logger.error(`更新章节进度失败 [用户ID: ${userId}, 课程ID: ${courseId}, 章节ID: ${chapterId}]:`, error);
    throw error;
  }
};

/**
 * 获取章节进度
 */
export const getChapterProgress = async (
  userId: string,
  courseId: string,
  chapterId: string
): Promise<IProgress | null> => {
  try {
    const progress = await ProgressModel.findOne({
      userId: new mongoose.Types.ObjectId(userId),
      courseId: new mongoose.Types.ObjectId(courseId),
      chapterId: new mongoose.Types.ObjectId(chapterId)
    });
    
    return progress;
  } catch (error) {
    logger.error(`获取章节进度失败 [用户ID: ${userId}, 课程ID: ${courseId}, 章节ID: ${chapterId}]:`, error);
    throw error;
  }
};

/**
 * 获取课程的所有章节进度
 */
export const getCourseProgress = async (
  userId: string,
  courseId: string
): Promise<IProgress[]> => {
  try {
    const progress = await ProgressModel.find({
      userId: new mongoose.Types.ObjectId(userId),
      courseId: new mongoose.Types.ObjectId(courseId)
    }).sort({ 'chapterId': 1 });
    
    return progress;
  } catch (error) {
    logger.error(`获取课程进度失败 [用户ID: ${userId}, 课程ID: ${courseId}]:`, error);
    throw error;
  }
};

/**
 * 更新注册的整体进度
 */
export const updateEnrollmentProgress = async (
  userId: string,
  courseId: string
): Promise<IEnrollment> => {
  try {
    // 获取课程信息
    const course = await CourseModel.findById(courseId);
    
    if (!course) {
      throw new ApiError(404, `未找到ID为 ${courseId} 的课程`);
    }
    
    // 获取完成的章节数
    const completedChaptersCount = await ProgressModel.countDocuments({
      userId: new mongoose.Types.ObjectId(userId),
      courseId: new mongoose.Types.ObjectId(courseId),
      status: ChapterStatus.COMPLETED
    });
    
    // 计算完成百分比
    const totalChapters = course.chapters.length;
    const percentageCompleted = totalChapters > 0 
      ? Math.round((completedChaptersCount / totalChapters) * 100) 
      : 0;
    
    // 更新注册记录
    const enrollment = await EnrollmentModel.findOne({
      userId: new mongoose.Types.ObjectId(userId),
      courseId: new mongoose.Types.ObjectId(courseId)
    });
    
    if (!enrollment) {
      throw new ApiError(404, '未找到课程注册记录');
    }
    
    enrollment.progress = {
      completedChapters: completedChaptersCount,
      totalChapters,
      percentageCompleted
    };
    
    enrollment.lastAccessedAt = new Date();
    
    // 如果所有章节都已完成，自动将注册状态更新为已完成
    if (completedChaptersCount === totalChapters && totalChapters > 0) {
      enrollment.status = EnrollmentStatus.COMPLETED;
      enrollment.completedAt = new Date();
      
      // 如果课程有证书功能，生成证书
      if (!enrollment.certificate || !enrollment.certificate.issued) {
        enrollment.certificate = {
          issued: true,
          issuedAt: new Date(),
          certificateUrl: await generateCertificate(userId, courseId)
        };
      }
    }
    
    await enrollment.save();
    return enrollment;
  } catch (error) {
    logger.error(`更新注册进度失败 [用户ID: ${userId}, 课程ID: ${courseId}]:`, error);
    throw error;
  }
};

/**
 * 生成课程完成证书
 */
export const generateCertificate = async (
  userId: string,
  courseId: string
): Promise<string> => {
  try {
    // 这里实现证书生成逻辑
    // 例如：生成PDF证书并保存到服务器，返回URL
    
    // 模拟生成证书URL
    const certificateUrl = `/certificates/${userId}/${courseId}/${Date.now()}.pdf`;
    
    return certificateUrl;
  } catch (error) {
    logger.error(`生成证书失败 [用户ID: ${userId}, 课程ID: ${courseId}]:`, error);
    throw error;
  }
};

/**
 * 提交课程评价
 */
export const submitCourseReview = async (
  userId: string,
  courseId: string,
  rating: number,
  comment?: string
): Promise<IReview> => {
  try {
    // 检查用户是否已注册并完成此课程
    const enrollment = await EnrollmentModel.findOne({
      userId: new mongoose.Types.ObjectId(userId),
      courseId: new mongoose.Types.ObjectId(courseId)
    });
    
    if (!enrollment) {
      throw new ApiError(400, '您尚未注册此课程，无法评价');
    }
    
    // 检查是否已经评价过
    const existingReview = await ReviewModel.findOne({
      userId: new mongoose.Types.ObjectId(userId),
      courseId: new mongoose.Types.ObjectId(courseId)
    });
    
    if (existingReview) {
      // 更新现有评价
      existingReview.rating = rating;
      
      if (comment !== undefined) {
        existingReview.comment = comment;
      }
      
      await existingReview.save();
      
      // 更新课程的平均评分
      await updateCourseAverageRating(courseId);
      
      return existingReview;
    }
    
    // 创建新评价
    const review = new ReviewModel({
      userId: new mongoose.Types.ObjectId(userId),
      courseId: new mongoose.Types.ObjectId(courseId),
      rating,
      comment
    });
    
    await review.save();
    
    // 更新课程的平均评分和评价数量
    await CourseModel.findByIdAndUpdate(
      courseId,
      { $inc: { reviewCount: 1 } }
    );
    
    await updateCourseAverageRating(courseId);
    
    return review;
  } catch (error) {
    logger.error(`提交课程评价失败 [用户ID: ${userId}, 课程ID: ${courseId}]:`, error);
    throw error;
  }
};

/**
 * 获取课程评价
 */
export const getCourseReviews = async (
  courseId: string,
  limit: number = 20,
  skip: number = 0
): Promise<{ total: number; reviews: IReview[] }> => {
  try {
    const total = await ReviewModel.countDocuments({ courseId: new mongoose.Types.ObjectId(courseId) });
    const reviews = await ReviewModel.find({ courseId: new mongoose.Types.ObjectId(courseId) })
      .sort({ createdAt: -1 })
      .skip(skip)
      .limit(limit)
      .populate('userId', 'name avatar');
    
    return { total, reviews };
  } catch (error) {
    logger.error(`获取课程评价失败 [课程ID: ${courseId}]:`, error);
    throw error;
  }
};

/**
 * 更新课程的平均评分
 */
export const updateCourseAverageRating = async (courseId: string): Promise<void> => {
  try {
    // 聚合查询计算平均评分
    const result = await ReviewModel.aggregate([
      { $match: { courseId: new mongoose.Types.ObjectId(courseId) } },
      { $group: { _id: null, avgRating: { $avg: "$rating" } } }
    ]);
    
    let avgRating = 0;
    
    if (result.length > 0) {
      avgRating = parseFloat(result[0].avgRating.toFixed(1));
    }
    
    // 更新课程的平均评分
    await CourseModel.findByIdAndUpdate(
      courseId,
      { avgRating }
    );
  } catch (error) {
    logger.error(`更新课程平均评分失败 [课程ID: ${courseId}]:`, error);
    throw error;
  }
}; 