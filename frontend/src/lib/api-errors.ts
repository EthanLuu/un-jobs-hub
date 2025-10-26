/**
 * Enhanced API error types and utilities
 */

export enum APIErrorCode {
  NETWORK_ERROR = 'NETWORK_ERROR',
  TIMEOUT_ERROR = 'TIMEOUT_ERROR',
  AUTH_ERROR = 'AUTH_ERROR',
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  NOT_FOUND = 'NOT_FOUND',
  SERVER_ERROR = 'SERVER_ERROR',
  UNKNOWN_ERROR = 'UNKNOWN_ERROR',
}

export interface APIErrorDetail {
  field?: string;
  message: string;
  code?: string;
}

export class APIError extends Error {
  code: APIErrorCode;
  statusCode?: number;
  details?: APIErrorDetail[];
  retryable: boolean;

  constructor(
    message: string,
    code: APIErrorCode = APIErrorCode.UNKNOWN_ERROR,
    statusCode?: number,
    details?: APIErrorDetail[],
    retryable: boolean = false
  ) {
    super(message);
    this.name = 'APIError';
    this.code = code;
    this.statusCode = statusCode;
    this.details = details;
    this.retryable = retryable;
  }

  static fromResponse(response: Response, errorData?: any): APIError {
    let code = APIErrorCode.UNKNOWN_ERROR;
    let retryable = false;
    let details: APIErrorDetail[] | undefined;

    // Determine error code and retryability based on status
    if (response.status >= 500) {
      code = APIErrorCode.SERVER_ERROR;
      retryable = true;
    } else if (response.status === 401) {
      code = APIErrorCode.AUTH_ERROR;
    } else if (response.status === 404) {
      code = APIErrorCode.NOT_FOUND;
    } else if (response.status === 422 || response.status === 400) {
      code = APIErrorCode.VALIDATION_ERROR;
    }

    // Extract error message and details
    let message = 'An error occurred';
    if (errorData) {
      if (typeof errorData.detail === 'string') {
        message = errorData.detail;
      } else if (Array.isArray(errorData.detail)) {
        // FastAPI validation errors
        details = errorData.detail.map((err: any) => ({
          field: err.loc ? err.loc.join('.') : undefined,
          message: err.msg || err.message || String(err),
          code: err.type,
        }));
        if (details && details.length > 0) {
          message = details.map(d => d.message).join(', ');
        }
      } else if (errorData.message) {
        message = errorData.message;
      } else if (errorData.error) {
        message = errorData.error;
      }
    } else {
      message = response.statusText || 'Request failed';
    }

    return new APIError(message, code, response.status, details, retryable);
  }

  static networkError(): APIError {
    return new APIError(
      'Network error. Please check your internet connection.',
      APIErrorCode.NETWORK_ERROR,
      undefined,
      undefined,
      true // Network errors are retryable
    );
  }

  static timeoutError(): APIError {
    return new APIError(
      'Request timed out. Please try again.',
      APIErrorCode.TIMEOUT_ERROR,
      undefined,
      undefined,
      true // Timeout errors are retryable
    );
  }

  getUserMessage(): string {
    // Return user-friendly messages
    switch (this.code) {
      case APIErrorCode.NETWORK_ERROR:
        return 'Unable to connect. Please check your internet connection.';
      case APIErrorCode.TIMEOUT_ERROR:
        return 'Request timed out. Please try again.';
      case APIErrorCode.AUTH_ERROR:
        return 'Authentication failed. Please log in again.';
      case APIErrorCode.NOT_FOUND:
        return 'The requested resource was not found.';
      case APIErrorCode.SERVER_ERROR:
        return 'Server error. Please try again later.';
      case APIErrorCode.VALIDATION_ERROR:
        return this.message; // Validation messages are usually user-friendly
      default:
        return this.message || 'An unexpected error occurred.';
    }
  }

  toJSON() {
    return {
      name: this.name,
      message: this.message,
      code: this.code,
      statusCode: this.statusCode,
      details: this.details,
      retryable: this.retryable,
    };
  }
}

/**
 * Retry utility for failed requests
 */
export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  options: {
    maxRetries?: number;
    initialDelay?: number;
    maxDelay?: number;
    shouldRetry?: (error: any) => boolean;
  } = {}
): Promise<T> {
  const {
    maxRetries = 3,
    initialDelay = 1000,
    maxDelay = 10000,
    shouldRetry = (error) => error instanceof APIError && error.retryable,
  } = options;

  let lastError: any;
  let delay = initialDelay;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;

      // Don't retry on last attempt or if error is not retryable
      if (attempt === maxRetries || !shouldRetry(error)) {
        throw error;
      }

      // Wait before retrying with exponential backoff
      await new Promise(resolve => setTimeout(resolve, delay));
      delay = Math.min(delay * 2, maxDelay);
    }
  }

  throw lastError;
}

/**
 * Timeout utility for requests
 */
export function withTimeout<T>(
  promise: Promise<T>,
  timeoutMs: number
): Promise<T> {
  return Promise.race([
    promise,
    new Promise<T>((_, reject) =>
      setTimeout(() => reject(APIError.timeoutError()), timeoutMs)
    ),
  ]);
}
