"use client";

import { useState } from "react";
import useSWR from "swr";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { api, Job } from "@/lib/api";
import { Sparkles, AlertCircle, TrendingUp, FileText } from "lucide-react";
import Link from "next/link";
import { RecommendationCard } from "@/components/recommendations/recommendation-card";
import { ResumeInfo } from "@/components/recommendations/resume-info";

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
      <ResumeInfo resume={activeResume} />

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
            return (
              <RecommendationCard
                key={match.job_id}
                match={match}
                job={job}
              />
            );
          })}
        </div>
      )}
    </div>
  );
}

