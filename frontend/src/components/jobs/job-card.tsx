"use client";

import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { BookmarkButton } from "@/components/jobs/bookmark-button";
import { MapPin, Calendar, Briefcase, GraduationCap, TrendingUp } from "lucide-react";
import Link from 'next/link';
import { formatDate, getDaysUntilDeadline } from "@/lib/utils";

interface JobCardProps {
  job: {
    id: number;
    title: string;
    organization: string;
    description: string;
    location?: string;
    grade?: string;
    contract_type?: string;
    education_level?: string;
    years_of_experience?: number;
    deadline?: string;
    apply_url?: string;
  };
  viewMode?: "list" | "grid" | "masonry";
}

export function JobCard({ job, viewMode = "list" }: JobCardProps) {
  const daysLeft = job.deadline ? getDaysUntilDeadline(job.deadline) : null;

  // Validate grade - should be in format like P-3, G-5, D-1, NO-A, etc.
  const isValidGrade = (grade: string | undefined): boolean => {
    if (!grade) return false;
    const gradePattern = /^(P-\d+|G-\d+|D-\d+|NO-[A-Z]|FS-\d+|L-\d+|GS-\d+|UG)$/i;
    return gradePattern.test(grade.trim());
  };

  const isCardMode = viewMode === "grid" || viewMode === "masonry";

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      whileHover={{ y: -4 }}
    >
      <Card className={`transition-shadow hover:shadow-md ${viewMode === "masonry" ? "masonry-card" : ""} h-full`}>
      <CardHeader>
        <div className={`flex items-start justify-between gap-2 ${isCardMode ? "flex-col" : ""}`}>
          <div className="flex-1">
            <div className="flex items-start justify-between gap-2">
              <CardTitle className="mb-2 flex-1">
                <Link
                  href={`/jobs/${job.id}`}
                  className="hover:text-primary line-clamp-2"
                >
                  {job.title}
                </Link>
              </CardTitle>
              <BookmarkButton jobId={job.id} />
            </div>
            <p className="text-sm font-medium text-primary">
              {job.organization}
            </p>
          </div>
          {daysLeft !== null && (
            <span
              className={`rounded-full px-3 py-1 text-xs font-medium whitespace-nowrap ${
                daysLeft <= 7
                  ? "bg-destructive/10 text-destructive"
                  : "bg-primary/10 text-primary"
              }`}
            >
              {daysLeft}d left
            </span>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <p className={`mb-4 text-sm text-muted-foreground ${isCardMode ? "line-clamp-3" : "line-clamp-2"}`}>
          {job.description}
        </p>
        <div className={`flex flex-wrap gap-x-4 gap-y-2 text-sm ${isCardMode ? "flex-col" : ""}`}>
          {job.location && (
            <div className="flex items-center gap-1 text-muted-foreground">
              <MapPin className="h-4 w-4 flex-shrink-0" />
              <span className="truncate">{job.location}</span>
            </div>
          )}
          {isValidGrade(job.grade) && (
            <div className="flex items-center gap-1 text-muted-foreground">
              <Briefcase className="h-4 w-4 flex-shrink-0" />
              <span>{job.grade}</span>
            </div>
          )}
          {job.contract_type && (
            <div className="flex items-center gap-1 text-muted-foreground">
              <Briefcase className="h-4 w-4 flex-shrink-0" />
              <span>{job.contract_type}</span>
            </div>
          )}
          {job.education_level && (
            <div className="flex items-center gap-1 text-muted-foreground">
              <GraduationCap className="h-4 w-4 flex-shrink-0" />
              <span>{job.education_level}</span>
            </div>
          )}
          {job.years_of_experience !== undefined && job.years_of_experience !== null && (
            <div className="flex items-center gap-1 text-muted-foreground">
              <TrendingUp className="h-4 w-4 flex-shrink-0" />
              <span>{job.years_of_experience}+ yrs</span>
            </div>
          )}
          {job.deadline && (
            <div className="flex items-center gap-1 text-muted-foreground">
              <Calendar className="h-4 w-4 flex-shrink-0" />
              <span>{formatDate(job.deadline)}</span>
            </div>
          )}
        </div>
        {isCardMode && (
          <div className="mt-4 pt-4 border-t">
            <Link href={`/jobs/${job.id}`}>
              <Button variant="outline" size="sm" className="w-full">
                View Details
              </Button>
            </Link>
          </div>
        )}
      </CardContent>
    </Card>
    </motion.div>
  );
}
