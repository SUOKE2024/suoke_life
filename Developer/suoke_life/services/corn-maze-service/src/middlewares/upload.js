/**
 * 文件上传中间件
 */
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');
const { createError } = require('./errorHandler');

// 确保上传目录存在
const uploadDir = path.join(__dirname, '../../uploads');
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir, { recursive: true });
}

// 配置存储
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    // 根据文件类型选择不同目录
    let targetDir = uploadDir;
    
    if (file.mimetype.startsWith('image/')) {
      targetDir = path.join(uploadDir, 'images');
    } else if (file.mimetype.startsWith('video/')) {
      targetDir = path.join(uploadDir, 'videos');
    } else if (file.mimetype === 'application/json') {
      targetDir = path.join(uploadDir, 'json');
    } else {
      targetDir = path.join(uploadDir, 'others');
    }
    
    // 确保目录存在
    if (!fs.existsSync(targetDir)) {
      fs.mkdirSync(targetDir, { recursive: true });
    }
    
    cb(null, targetDir);
  },
  filename: (req, file, cb) => {
    // 生成唯一文件名
    const uniqueName = `${uuidv4()}${path.extname(file.originalname)}`;
    cb(null, uniqueName);
  }
});

// 文件过滤器
const fileFilter = (req, file, cb) => {
  // 允许的文件类型
  const allowedTypes = [
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/webp',
    'video/mp4',
    'video/webm',
    'application/json'
  ];
  
  if (allowedTypes.includes(file.mimetype)) {
    cb(null, true);
  } else {
    cb(createError('不支持的文件类型', 415), false);
  }
};

// 大小限制 (单位: 字节)
const limits = {
  fileSize: 10 * 1024 * 1024, // 10MB
  files: 5 // 最多5个文件
};

// 创建multer实例
const upload = multer({
  storage,
  fileFilter,
  limits
});

// 内存存储配置 (用于图像处理前不存储到磁盘)
const memoryStorage = multer.memoryStorage();
const uploadToMemory = multer({
  storage: memoryStorage,
  fileFilter,
  limits
});

// 错误处理
const handleUploadError = (err, req, res, next) => {
  if (err instanceof multer.MulterError) {
    if (err.code === 'LIMIT_FILE_SIZE') {
      return next(createError('文件大小超过限制', 413));
    }
    if (err.code === 'LIMIT_FILE_COUNT') {
      return next(createError('文件数量超过限制', 413));
    }
    return next(createError(`上传错误: ${err.message}`, 400));
  }
  
  next(err);
};

module.exports = upload;
module.exports.single = upload.single;
module.exports.array = upload.array;
module.exports.fields = upload.fields;
module.exports.none = upload.none;
module.exports.any = upload.any;
module.exports.memoryStorage = uploadToMemory;
module.exports.handleUploadError = handleUploadError; 