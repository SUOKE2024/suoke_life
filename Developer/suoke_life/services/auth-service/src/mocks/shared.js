/**
 * 模拟 @suoke/shared 包
 */
module.exports = {
  utils: {
    responseHandler: {
      success: jest.fn((res, data, message, statusCode = 200) => {
        res.status(statusCode).json({
          success: true,
          data,
          message
        });
      }),
      error: jest.fn((res, message, statusCode = 400, errorCode = null) => {
        res.status(statusCode).json({
          success: false,
          message,
          errorCode
        });
      })
    },
    validators: {
      isValidEmail: jest.fn(email => {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
      }),
      isValidPhone: jest.fn(phone => {
        const regex = /^1[3-9]\d{9}$/;
        return regex.test(phone);
      }),
      isStrongPassword: jest.fn(password => {
        return password && password.length >= 8;
      }),
      sanitizeInput: jest.fn(input => {
        if (typeof input === 'string') {
          return input.trim();
        }
        return input;
      }),
      validateSchema: jest.fn((schema, data) => {
        return { isValid: true, errors: [] };
      })
    },
    errors: {
      ApiError: class ApiError extends Error {
        constructor(message, statusCode = 500, errorCode = null) {
          super(message);
          this.name = 'ApiError';
          this.statusCode = statusCode;
          this.errorCode = errorCode;
        }
      },
      ValidationError: class ValidationError extends Error {
        constructor(message, errors = []) {
          super(message);
          this.name = 'ValidationError';
          this.statusCode = 400;
          this.errors = errors;
        }
      },
      NotFoundError: class NotFoundError extends Error {
        constructor(message) {
          super(message);
          this.name = 'NotFoundError';
          this.statusCode = 404;
        }
      },
      UnauthorizedError: class UnauthorizedError extends Error {
        constructor(message) {
          super(message);
          this.name = 'UnauthorizedError';
          this.statusCode = 401;
        }
      },
      ForbiddenError: class ForbiddenError extends Error {
        constructor(message) {
          super(message);
          this.name = 'ForbiddenError';
          this.statusCode = 403;
        }
      }
    }
  },
  middleware: {
    errorHandler: jest.fn((err, req, res, next) => {
      const statusCode = err.statusCode || 500;
      const errorCode = err.errorCode || 'server_error';
      res.status(statusCode).json({
        success: false,
        message: err.message || 'Internal Server Error',
        errorCode
      });
    }),
    authenticate: jest.fn((req, res, next) => {
      req.user = { id: 'mock-user-id' };
      next();
    }),
    authorize: jest.fn((roles) => {
      return (req, res, next) => {
        next();
      };
    }),
    validateRequest: jest.fn((schema) => {
      return (req, res, next) => {
        next();
      };
    }),
    rateLimiter: jest.fn((options) => {
      return (req, res, next) => {
        next();
      };
    })
  },
  constants: {
    ERROR_CODES: {
      VALIDATION_ERROR: 'validation_error',
      AUTHENTICATION_ERROR: 'authentication_error',
      AUTHORIZATION_ERROR: 'authorization_error',
      NOT_FOUND_ERROR: 'not_found_error',
      SERVER_ERROR: 'server_error'
    },
    USER_ROLES: {
      ADMIN: 'admin',
      USER: 'user',
      GUEST: 'guest'
    },
    AUTH_TYPES: {
      EMAIL: 'email',
      PHONE: 'phone',
      SOCIAL: 'social',
      BIOMETRIC: 'biometric'
    }
  }
}; 