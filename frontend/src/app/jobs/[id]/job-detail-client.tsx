"use client";

import { useState } from "react";
import useSWR from "swr";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";
import {
  MapPin,
  Calendar,
  Briefcase,
  Globe,
  Clock,
  Heart,
  ExternalLink,
  ArrowLeft,
  Building2,
  Languages,
} from "lucide-react";
import Link from "next/link";
import { formatDate, getDaysUntilDeadline } from "@/lib/utils";

interface JobDetailClientProps {
  jobId: number;
}

export function JobDetailClient({ jobId }: JobDetailClientProps) {
  const [isFavorited, setIsFavorited] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const { data: job, error } = useSWR(`job-${jobId}`, () => api.getJob(jobId));

  const handleFavorite = async () => {
    setIsLoading(true);
    try {
      await api.addFavorite(jobId);
      setIsFavorited(true);
    } catch (error) {
      console.error("Failed to favorite job:", error);
      alert("Failed to add to favorites");
    } finally {
      setIsLoading(false);
    }
  };

  if (error) {
    return (
      <div className="container py-8">
        <Card>
          <CardContent className="py-8 text-center">
            <p className="text-destructive">Failed to load job. Please try again.</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!job) {
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

  const daysLeft = job.deadline ? getDaysUntilDeadline(job.deadline) : null;

  return (
    <div className="container py-8">
      <div className="mb-6">
        <Button variant="ghost" asChild>
          <Link href="/jobs">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Jobs
          </Link>
        </Button>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Main Content */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <div className="mb-4 flex flex-wrap gap-2">
                <Badge variant="secondary">{job.organization}</Badge>
                {job.category && <Badge variant="outline">{job.category}</Badge>}
                {job.grade && <Badge variant="outline">Grade: {job.grade}</Badge>}
                {daysLeft !== null && (
                  <Badge
                    variant={daysLeft <= 7 ? "destructive" : "default"}
                  >
                    {daysLeft}d left
                  </Badge>
                )}
              </div>
              <CardTitle className="text-3xl">{job.title}</CardTitle>
              <CardDescription className="text-base">
                Job ID: {job.job_id}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Key Details */}
              <div className="grid gap-4 sm:grid-cols-2">
                {job.location && (
                  <div className="flex items-start gap-3">
                    <MapPin className="mt-0.5 h-5 w-5 text-muted-foreground" />
                    <div>
                      <p className="text-sm font-medium">Location</p>
                      <p className="text-sm text-muted-foreground">{job.location}</p>
                    </div>
                  </div>
                )}
                {job.duty_station && (
                  <div className="flex items-start gap-3">
                    <Building2 className="mt-0.5 h-5 w-5 text-muted-foreground" />
                    <div>
                      <p className="text-sm font-medium">Duty Station</p>
                      <p className="text-sm text-muted-foreground">{job.duty_station}</p>
                    </div>
                  </div>
                )}
                {job.contract_type && (
                  <div className="flex items-start gap-3">
                    <Briefcase className="mt-0.5 h-5 w-5 text-muted-foreground" />
                    <div>
                      <p className="text-sm font-medium">Contract Type</p>
                      <p className="text-sm text-muted-foreground">{job.contract_type}</p>
                    </div>
                  </div>
                )}
                {job.deadline && (
                  <div className="flex items-start gap-3">
                    <Calendar className="mt-0.5 h-5 w-5 text-muted-foreground" />
                    <div>
                      <p className="text-sm font-medium">Application Deadline</p>
                      <p className="text-sm text-muted-foreground">
                        {formatDate(job.deadline)}
                      </p>
                    </div>
                  </div>
                )}
                {job.posted_date && (
                  <div className="flex items-start gap-3">
                    <Clock className="mt-0.5 h-5 w-5 text-muted-foreground" />
                    <div>
                      <p className="text-sm font-medium">Posted Date</p>
                      <p className="text-sm text-muted-foreground">
                        {formatDate(job.posted_date)}
                      </p>
                    </div>
                  </div>
                )}
                {job.remote_eligible && (
                  <div className="flex items-start gap-3">
                    <Globe className="mt-0.5 h-5 w-5 text-muted-foreground" />
                    <div>
                      <p className="text-sm font-medium">Remote Work</p>
                      <p className="text-sm text-muted-foreground">
                        {job.remote_eligible}
                      </p>
                    </div>
                  </div>
                )}
              </div>

              {/* Language Requirements */}
              {job.language_requirements &&
                Object.keys(job.language_requirements).length > 0 && (
                  <div>
                    <div className="mb-2 flex items-center gap-2">
                      <Languages className="h-5 w-5 text-muted-foreground" />
                      <h3 className="font-semibold">Language Requirements</h3>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {Object.entries(job.language_requirements).map(
                        ([lang, level]) => (
                          <Badge key={lang} variant="outline">
                            {lang}: {level}
                          </Badge>
                        )
                      )}
                    </div>
                  </div>
                )}

              {/* Description */}
              <div>
                <h3 className="mb-3 text-lg font-semibold">Job Description</h3>
                <div className="prose prose-sm max-w-none">
                  <p className="whitespace-pre-wrap text-sm leading-relaxed text-muted-foreground">
                    {job.description}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Apply Card */}
          <Card>
            <CardHeader>
              <CardTitle>Apply for this Position</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button className="w-full" size="lg" asChild>
                <a href={job.apply_url} target="_blank" rel="noopener noreferrer">
                  <ExternalLink className="mr-2 h-4 w-4" />
                  Apply on Official Site
                </a>
              </Button>
              <Button
                variant="outline"
                className="w-full"
                onClick={handleFavorite}
                disabled={isLoading || isFavorited}
              >
                <Heart
                  className={`mr-2 h-4 w-4 ${isFavorited ? "fill-current" : ""}`}
                />
                {isFavorited ? "Added to Favorites" : "Save to Favorites"}
              </Button>
            </CardContent>
          </Card>

          {/* Organization Info */}
          <Card>
            <CardHeader>
              <CardTitle>About {job.organization}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                {job.organization === "UN"
                  ? "The United Nations is an international organization founded in 1945 to promote peace, security, and cooperation among nations."
                  : job.organization === "UNDP"
                  ? "The United Nations Development Programme works in nearly 170 countries to eradicate poverty, reduce inequalities, and build resilience."
                  : job.organization === "UNICEF"
                  ? "UNICEF works in over 190 countries to save children's lives, defend their rights, and help them fulfill their potential."
                  : `${job.organization} is part of the United Nations system working towards global development and humanitarian goals.`}
              </p>
            </CardContent>
          </Card>

          {/* Quick Stats */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Stats</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Status</span>
                <Badge variant={job.is_active ? "default" : "secondary"}>
                  {job.is_active ? "Active" : "Closed"}
                </Badge>
              </div>
              {daysLeft !== null && (
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Days Left</span>
                  <span className="font-semibold">{daysLeft}</span>
                </div>
              )}
              {job.grade && (
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Grade</span>
                  <span className="font-semibold">{job.grade}</span>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

