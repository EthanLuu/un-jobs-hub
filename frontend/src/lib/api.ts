const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface Job {
  id: number;
  title: string;
  organization: string;
  job_id: string;
  description: string;
  responsibilities?: string;
  qualifications?: string;
  category?: string;
  grade?: string;
  contract_type?: string;
  location?: string;
  duty_station?: string;
  remote_eligible: string;
  language_requirements?: Record<string, string>;
  education_level?: string;
  years_of_experience?: number;
  apply_url: string;
  deadline?: string;
  posted_date?: string;
  source_url?: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
  last_scraped?: string;
}

export interface JobsResponse {
  jobs: Job[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

class APIClient {
  private baseURL: string;
  private token: string | null = null;

  constructor() {
    // Remove trailing slash from API URL to prevent double slashes
    this.baseURL = API_URL.replace(/\/$/, "");
    if (typeof window !== "undefined") {
      this.token = localStorage.getItem("token");
    }
  }

  setToken(token: string) {
    this.token = token;
    if (typeof window !== "undefined") {
      localStorage.setItem("token", token);
    }
  }

  clearToken() {
    this.token = null;
    if (typeof window !== "undefined") {
      localStorage.removeItem("token");
    }
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options.headers as Record<string, string>),
    };

    if (this.token) {
      headers["Authorization"] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || "An error occurred");
    }

    return response.json();
  }

  // Auth endpoints
  async login(email: string, password: string): Promise<AuthResponse> {
    const response = await this.request<AuthResponse>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    this.setToken(response.access_token);
    return response;
  }

  async register(
    email: string,
    username: string,
    password: string
  ): Promise<AuthResponse> {
    const response = await this.request<AuthResponse>("/api/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, username, password }),
    });
    this.setToken(response.access_token);
    return response;
  }

  // Jobs endpoints
  async getJobs(params?: Record<string, string | number>): Promise<JobsResponse> {
    const queryString = params
      ? "?" + new URLSearchParams(params as Record<string, string>).toString()
      : "";
    return this.request<JobsResponse>(`/api/jobs${queryString}`);
  }

  async getJob(id: number): Promise<Job> {
    return this.request<Job>(`/api/jobs/${id}`);
  }

  async getFilterOptions() {
    return this.request<{
      organizations: string[];
      categories: string[];
      grades: string[];
      locations: string[];
      education_levels: string[];
      experience_range: { min: number; max: number };
    }>("/api/jobs/filters/options");
  }

  // Favorites endpoints
  async getFavorites(): Promise<any[]> {
    return this.request("/api/favorites");
  }

  async addFavorite(jobId: number, notes?: string): Promise<any> {
    return this.request("/api/favorites", {
      method: "POST",
      body: JSON.stringify({ job_id: jobId, notes }),
    });
  }

  async removeFavorite(favoriteId: number): Promise<void> {
    return this.request(`/api/favorites/${favoriteId}`, {
      method: "DELETE",
    });
  }

  // Resume endpoints
  async getResumes(): Promise<any[]> {
    return this.request("/api/resume");
  }

  async getResume(resumeId: number): Promise<any> {
    return this.request(`/api/resume/${resumeId}`);
  }

  async uploadResume(file: File): Promise<any> {
    const formData = new FormData();
    formData.append("file", file);

    const headers: Record<string, string> = {};
    if (this.token) {
      headers["Authorization"] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${this.baseURL}/api/resume/upload`, {
      method: "POST",
      headers,
      body: formData,
    });

    if (!response.ok) {
      throw new Error("Failed to upload resume");
    }

    return response.json();
  }

  async deleteResume(resumeId: number): Promise<void> {
    return this.request(`/api/resume/${resumeId}`, {
      method: "DELETE",
    });
  }

  // Match endpoints
  async matchResumeToJob(resumeId: number, jobId?: number): Promise<any> {
    return this.request("/api/match", {
      method: "POST",
      body: JSON.stringify({ resume_id: resumeId, job_id: jobId }),
    });
  }

  async getRecommendations(): Promise<any> {
    // Get user's active resume and match against all jobs
    const resumes = await this.getResumes();
    const activeResume = resumes.find((r) => r.is_active);
    
    if (!activeResume) {
      throw new Error("No active resume found");
    }

    return this.matchResumeToJob(activeResume.id);
  }

  // User endpoints
  async getCurrentUser(): Promise<User> {
    return this.request("/api/auth/me");
  }

  async updateProfile(data: {
    full_name?: string;
    username?: string;
  }): Promise<User> {
    return this.request("/api/auth/profile", {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }
}

export const api = new APIClient();



