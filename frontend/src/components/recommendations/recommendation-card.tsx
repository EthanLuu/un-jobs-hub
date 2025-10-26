"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { MapPin, Calendar, Briefcase, CheckCircle, AlertCircle } from "lucide-react";
import { Link } from '@/i18n/navigation';
import { formatDate, getDaysUntilDeadline } from "@/lib/utils";

interface MatchResponse {
  job_id: number;
  match_score: number;
  missing_keywords: string[];
  matching_keywords: string[];
  recommendation: string;
}

interface Job {
  id: number;
  title: string;
  organization: string;
  description: string;
  location?: string;
  grade?: string;
  deadline?: string;
  apply_url?: string;
}

interface RecommendationCardProps {
  match: MatchResponse;
  job: Job;
}

export function RecommendationCard({ match, job }: RecommendationCardProps) {
  const daysLeft = job.deadline ? getDaysUntilDeadline(job.deadline) : null;

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

  const matchBadge = getMatchBadge(match.match_score);

  return (
    <Card className="overflow-hidden transition-shadow hover:shadow-lg">
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
}
