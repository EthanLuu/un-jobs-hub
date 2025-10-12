# UN Jobs Hub Features

## Overview

UN Jobs Hub is a comprehensive platform for discovering and applying to United Nations job opportunities. The platform features AI-powered job matching, resume analysis, and personalized recommendations.

## Core Features

### 1. Job Search & Discovery

**Location:** `/jobs`

- **Advanced Search**: Search by keywords, organization, location, grade, and more
- **Filtering**: Filter jobs by UN organizations (UN, UNDP, UNICEF, WHO, FAO, UNOPS)
- **Pagination**: Browse through thousands of job listings efficiently
- **Job Details**: View comprehensive job information including:
  - Job title, organization, and description
  - Location and duty station
  - Contract type and grade
  - Application deadline
  - Remote work eligibility
  - Language requirements

**Features:**
- Real-time search with instant results
- Organization-specific filtering
- Deadline indicators (days left to apply)
- Responsive card-based UI
- Direct links to official application pages

### 2. User Profile Management

**Location:** `/profile`

The profile page allows users to manage their account information and resumes in a tabbed interface.

#### Profile Tab
- View and edit user information:
  - Email (read-only)
  - Username
  - Full name
  - Member since date
- Update profile information with validation
- Real-time profile updates

#### Resumes Tab
- **Upload Resume**: Upload PDF or DOCX files (max 10MB)
- **Resume Parsing**: Automatic extraction of:
  - Skills and keywords
  - Years of experience
  - Education history
  - Key achievements
- **Resume Management**:
  - View all uploaded resumes
  - See parsed skills and experience
  - Active resume indicator
  - Delete unwanted resumes
- **Visual Indicators**:
  - Active resume badge
  - Upload date
  - File type
  - Extracted skills chips

### 3. AI-Powered Job Recommendations

**Location:** `/recommendations`

Personalized job recommendations based on resume analysis using machine learning algorithms.

#### Features

**Resume Analysis Display**:
- Shows currently active resume
- Displays extracted skills
- Shows years of experience
- Visual skill badges

**Match Scoring**:
- **Excellent Match**: 80%+ score (green badge)
- **Good Match**: 60-79% score (yellow badge)
- **Fair Match**: Below 60% (orange badge)
- Visual progress bars for match percentage

**Detailed Match Information**:
- **Matching Skills**: Skills from your resume that match job requirements
  - Displayed as green badges
  - Shows count of matching skills
- **Skills to Develop**: Job requirements not in your resume
  - Displayed as orange outlined badges
  - Helps identify gaps in qualifications
- **AI Recommendation**: Personalized advice for each job match
  - Context-aware suggestions
  - Actionable recommendations

**Job Cards Include**:
- Match score with visual indicator
- Job title, organization, and description
- Location and deadline information
- Matching vs. missing keywords comparison
- Direct "View Details" and "Apply Now" buttons

**Actions**:
- Refresh recommendations button
- View full job details
- Apply directly from recommendations
- Save to favorites

### 4. Job Detail Page

**Location:** `/jobs/[id]`

Comprehensive job information display with application tools.

#### Main Content
- Full job description
- Organization information
- Key details grid:
  - Location and duty station
  - Contract type and grade
  - Application deadline
  - Posted date
  - Remote eligibility
- Language requirements with proficiency levels

#### Sidebar Features
- **Apply Card**:
  - Direct link to official application
  - Save to favorites button
- **Organization Info**: Background about the UN organization
- **Quick Stats**: Status, days left, grade overview

### 5. Favorites System

**Backend API:** `/api/favorites`

- Add jobs to favorites with optional notes
- View saved job listings
- Remove jobs from favorites
- Quick access to saved opportunities

## Technical Features

### Frontend Technologies

- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS with custom components
- **UI Components**: Radix UI primitives
  - Tabs for navigation
  - Progress bars for match scores
  - Badges for labels
  - Cards for content organization
- **State Management**: SWR for data fetching and caching
- **Icons**: Lucide React

### Backend Technologies

- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens
- **Resume Parsing**: Custom parser for PDF/DOCX files
- **Matching Algorithm**: Keyword-based with scoring

### API Endpoints

#### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user
- `PUT /api/auth/profile` - Update profile

#### Jobs
- `GET /api/jobs` - List jobs with filters and pagination
- `GET /api/jobs/{id}` - Get job details
- `GET /api/jobs/filters/options` - Get filter options

#### Resumes
- `GET /api/resume` - List user resumes
- `POST /api/resume/upload` - Upload and parse resume
- `GET /api/resume/{id}` - Get resume details
- `DELETE /api/resume/{id}` - Delete resume

#### Matching
- `POST /api/match` - Match resume to jobs
- `GET /api/match/job/{job_id}` - Match active resume to specific job

#### Favorites
- `GET /api/favorites` - List favorites
- `POST /api/favorites` - Add favorite
- `DELETE /api/favorites/{id}` - Remove favorite

## User Workflows

### Getting Started
1. Register for an account
2. Upload your resume (PDF or DOCX)
3. System automatically parses your skills and experience
4. Browse recommendations tailored to your profile

### Finding Jobs
1. Browse all jobs at `/jobs`
2. Use search to find specific positions
3. Filter by organization or other criteria
4. View detailed job information
5. Save interesting jobs to favorites

### Getting Recommendations
1. Ensure you have an active resume uploaded
2. Visit `/recommendations`
3. Review AI-matched jobs with scores
4. See which skills you match and which to develop
5. Read personalized recommendations
6. Apply directly or save for later

### Managing Profile
1. Go to `/profile`
2. Update your personal information in Profile tab
3. Manage resumes in Resumes tab
4. Upload new versions as needed
5. Delete old resumes

## Design Philosophy

### User Experience
- **Clean & Modern**: Minimal, professional design
- **Responsive**: Works on desktop, tablet, and mobile
- **Intuitive**: Clear navigation and information hierarchy
- **Fast**: Optimized loading and caching
- **Accessible**: WCAG compliant components

### Visual Indicators
- **Color Coding**: Match scores use traffic light colors
- **Badges**: Quick status and category identification
- **Progress Bars**: Visual match percentage display
- **Icons**: Contextual icons for better scanning

### Information Architecture
- **Hierarchical**: Important info first
- **Scannable**: Easy to find key details
- **Actionable**: Clear calls-to-action
- **Contextual**: Relevant information grouped together

## Future Enhancements

Potential features for future releases:

1. **Email Notifications**: Alerts for new matching jobs
2. **Application Tracking**: Track application status
3. **Cover Letter Generator**: AI-assisted cover letters
4. **Interview Preparation**: Tips based on job requirements
5. **Skill Development**: Learning resources for missing skills
6. **Advanced Filters**: More granular job filtering
7. **Saved Searches**: Save and monitor search criteria
8. **Mobile App**: Native iOS and Android apps
9. **Multi-language**: Support for UN languages
10. **Export Features**: Export job lists and match reports

## Support

For issues or questions:
- Check the documentation
- Review the SETUP_CHECKLIST.md
- See QUICKSTART.md for getting started
- Refer to DEPLOYMENT.md for deployment info

## License

See LICENSE file for details.

