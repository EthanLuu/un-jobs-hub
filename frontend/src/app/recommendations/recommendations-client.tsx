"use client";

import { useState } from "react";
import useSWR from "swr";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { api, Job } from "@/lib/api";
import { Sparkles, MapPin, Calendar, Briefcase, CheckCircle, AlertCircle, TrendingUp, FileText } from "lucide-react";
import Link from "next/link";
import { formatDate, getDaysUntilDeadline } from "@/lib/utils";

interface MatchResponse {
  job_id: number;
  match_score: number;
  missing_keywords: string[];
  matching_keywords: string[];
  recommendation: string;
}

interface MatchResult {
  matches: MatchResponse[];
  resume_id: number;
}

export function RecommendationsClient() {
  const [loadingMatches, setLoadingMatches] = useState(false);
  
  const { data: resumes } = useSWR(
    "resumes",
    async () => {
      try {
        return await api.getResumes();
      } catch (error) {
        // Return empty array if not authenticated
        return [];
      }
    }
  );

  const { data: matchData, error: matchError, mutate: mutateMatches } = useSWR<MatchResult | null>(
    resumes && resumes.find((r: any) => r.is_active) ? "recommendations" : null,
    async () => {
      try {
        return await api.getRecommendations();
      } catch (error) {
        console.error("Failed to get recommendations:", error);
        return null;
      }
    }
  );

  const { data: jobs, error: jobsError } = useSWR(
    matchData ? "jobs-for-matches" : null,
    async () => {
      if (!matchData?.matches) return [];
      const jobIds = matchData.matches.map(m => m.job_id);
      const jobPromises = jobIds.map(id => api.getJob(id));
      return Promise.all(jobPromises);
    }
  );

  const handleRefreshRecommendations = async () => {
    setLoadingMatches(true);
    try {
      await mutateMatches();
    } finally {
      setLoadingMatches(false);
    }
  };

  const getMatchColor = (score: number) => {
    if (score >= 80) return "text-green-600";
    if (score >= 60) return "text-yellow-600";
    return "text-orange-600";
  };

  const getMatchBadge = (score: number) => {
    if (score >= 80) return { label: "Excellent Match", variant: "default" as const };
    if (score >= 60) return { label: "Good Match", variant: "secondary" as const };
    return { label: "Fair Match", variant: "outline" as const };
  };

  if (matchError || jobsError) {
    return (
      <div className="container py-8">
        <Card>
          <CardContent className="py-8 text-center">
            <AlertCircle className="mx-auto mb-4 h-12 w-12 text-destructive" />
            <p className="text-destructive">Failed to load recommendations. Please try again.</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!resumes) {
    return (
      <div className="container py-8">
        <Card>
          <CardContent className="py-8 text-center">
            <p className="text-muted-foreground">Loading...</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const activeResume = resumes.find((r: any) => r.is_active);

  if (!activeResume) {
    return (
      <div className="container py-8">
        <div className="mb-8">
          <h1 className="mb-2 text-4xl font-bold">Job Recommendations</h1>
          <p className="text-muted-foreground">
            Get personalized job recommendations based on your resume
          </p>
        </div>

        <Card>
          <CardContent className="py-12 text-center">
            <FileText className="mx-auto mb-4 h-16 w-16 text-muted-foreground" />
            <h2 className="mb-2 text-xl font-semibold">No Resume Found</h2>
            <p className="mb-6 text-muted-foreground">
              Upload your resume to get personalized job recommendations
            </p>
            <Button asChild>
              <Link href="/profile">Upload Resume</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const matchesWithJobs = matchData?.matches.map((match, index) => ({
    match,
    job: jobs?.[index],
  })).filter(item => item.job) || [];

  return (
    <div className="container py-8">
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="mb-2 flex items-center gap-2 text-4xl font-bold">
              <Sparkles className="h-8 w-8 text-primary" />
              Job Recommendations
            </h1>
            <p className="text-muted-foreground">
              Personalized opportunities based on your resume
            </p>
          </div>
          <Button onClick={handleRefreshRecommendations} disabled={loadingMatches}>
            <TrendingUp className="mr-2 h-4 w-4" />
            {loadingMatches ? "Refreshing..." : "Refresh"}
          </Button>
        </div>
      </div>

      {/* Resume Info */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="text-lg">Analyzing Resume</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4">
            <div className="rounded-lg bg-primary/10 p-3">
              <FileText className="h-6 w-6 text-primary" />
            </div>
            <div className="flex-1">
              <p className="font-medium">{activeResume.filename}</p>
              <div className="mt-1 flex flex-wrap gap-2">
                {activeResume.skills && activeResume.skills.length > 0 && (
                  <>
                    {activeResume.skills.slice(0, 6).map((skill: string) => (
                      <Badge key={skill} variant="outline" className="text-xs">
                        {skill}
                      </Badge>
                    ))}
                    {activeResume.skills.length > 6 && (
                      <Badge variant="outline" className="text-xs">
                        +{activeResume.skills.length - 6} more
                      </Badge>
                    )}
                  </>
                )}
              </div>
            </div>
            {activeResume.experience_years && (
              <div className="flex items-center gap-2 rounded-lg border px-4 py-2">
                <Briefcase className="h-5 w-5 text-muted-foreground" />
                <div>
                  <p className="text-xs text-muted-foreground">Experience</p>
                  <p className="font-semibold">{activeResume.experience_years} years</p>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Matches */}
      {!matchData || !jobs ? (
        <Card>
          <CardContent className="py-8 text-center">
            <p className="text-muted-foreground">Loading recommendations...</p>
          </CardContent>
        </Card>
      ) : matchesWithJobs.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <AlertCircle className="mx-auto mb-4 h-12 w-12 text-muted-foreground" />
            <h2 className="mb-2 text-xl font-semibold">No Matches Found</h2>
            <p className="text-muted-foreground">
              We couldn't find any matching jobs at the moment. Try again later or update your resume.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-6">
          {matchesWithJobs.map(({ match, job }) => {
            if (!job) return null;
            
            const daysLeft = job.deadline ? getDaysUntilDeadline(job.deadline) : null;
            const matchBadge = getMatchBadge(match.match_score);

            return (
              <Card key={match.job_id} className="overflow-hidden transition-shadow hover:shadow-lg">
                <CardHeader className="bg-gradient-to-r from-primary/5 to-primary/10">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="mb-2 flex items-center gap-2">
                        <Badge variant={matchBadge.variant}>
                          {matchBadge.label}
                        </Badge>
                        {daysLeft !== null && daysLeft <= 7 && (
                          <Badge variant="destructive">
                            {daysLeft}d left
                          </Badge>
                        )}
                      </div>
                      <CardTitle className="mb-2">
                        <Link href={`/jobs/${job.id}`} className="hover:text-primary">
                          {job.title}
                        </Link>
                      </CardTitle>
                      <p className="text-sm font-medium text-primary">{job.organization}</p>
                    </div>
                    <div className="text-right">
                      <div className={`text-3xl font-bold ${getMatchColor(match.match_score)}`}>
                        {Math.round(match.match_score)}%
                      </div>
                      <p className="text-xs text-muted-foreground">Match Score</p>
                    </div>
                  </div>
                  
                  <Progress value={match.match_score} className="mt-4" />
                </CardHeader>

                <CardContent className="pt-6">
                  <p className="mb-4 line-clamp-2 text-sm text-muted-foreground">
                    {job.description}
                  </p>

                  {/* Job Details */}
                  <div className="mb-4 flex flex-wrap gap-4 text-sm">
                    {job.location && (
                      <div className="flex items-center gap-1 text-muted-foreground">
                        <MapPin className="h-4 w-4" />
                        <span>{job.location}</span>
                      </div>
                    )}
                    {job.grade && (
                      <div className="flex items-center gap-1 text-muted-foreground">
                        <Briefcase className="h-4 w-4" />
                        <span>Grade: {job.grade}</span>
                      </div>
                    )}
                    {job.deadline && (
                      <div className="flex items-center gap-1 text-muted-foreground">
                        <Calendar className="h-4 w-4" />
                        <span>Deadline: {formatDate(job.deadline)}</span>
                      </div>
                    )}
                  </div>

                  {/* Matching Keywords */}
                  {match.matching_keywords.length > 0 && (
                    <div className="mb-4">
                      <div className="mb-2 flex items-center gap-2 text-sm font-medium">
                        <CheckCircle className="h-4 w-4 text-green-600" />
                        <span>Matching Skills ({match.matching_keywords.length})</span>
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {match.matching_keywords.slice(0, 8).map((keyword) => (
                          <Badge key={keyword} variant="secondary" className="bg-green-50 text-green-700">
                            {keyword}
                          </Badge>
                        ))}
                        {match.matching_keywords.length > 8 && (
                          <Badge variant="secondary" className="bg-green-50 text-green-700">
                            +{match.matching_keywords.length - 8} more
                          </Badge>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Missing Keywords */}
                  {match.missing_keywords.length > 0 && (
                    <div className="mb-4">
                      <div className="mb-2 flex items-center gap-2 text-sm font-medium">
                        <AlertCircle className="h-4 w-4 text-orange-600" />
                        <span>Skills to Develop ({match.missing_keywords.length})</span>
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {match.missing_keywords.slice(0, 8).map((keyword) => (
                          <Badge key={keyword} variant="outline" className="border-orange-200 text-orange-700">
                            {keyword}
                          </Badge>
                        ))}
                        {match.missing_keywords.length > 8 && (
                          <Badge variant="outline" className="border-orange-200 text-orange-700">
                            +{match.missing_keywords.length - 8} more
                          </Badge>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Recommendation */}
                  {match.recommendation && (
                    <div className="rounded-lg bg-muted/50 p-4">
                      <p className="mb-1 text-sm font-medium">AI Recommendation</p>
                      <p className="text-sm text-muted-foreground">{match.recommendation}</p>
                    </div>
                  )}

                  <div className="mt-4 flex gap-2">
                    <Button asChild className="flex-1">
                      <Link href={`/jobs/${job.id}`}>View Details</Link>
                    </Button>
                    <Button asChild variant="outline">
                      <a href={job.apply_url} target="_blank" rel="noopener noreferrer">
                        Apply Now
                      </a>
                    </Button>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}

