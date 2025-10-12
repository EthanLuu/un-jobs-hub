"use client";

import Link from "next/link";
import useSWR from "swr";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import { Briefcase, MapPin, Calendar, ArrowRight } from "lucide-react";
import { formatDate, getDaysUntilDeadline } from "@/lib/utils";

export function FeaturedJobs() {
  const { data, error, isLoading } = useSWR("/api/jobs?page=1&page_size=6", () =>
    api.getJobs({ page: 1, page_size: 6 })
  );

  if (isLoading) {
    return (
      <section className="py-16">
        <div className="container">
          <div className="mb-8 text-center">
            <h2 className="mb-3 text-3xl font-bold">Featured Jobs</h2>
            <p className="text-muted-foreground">
              Latest opportunities in the UN system
            </p>
          </div>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {[...Array(6)].map((_, i) => (
              <Card key={i} className="animate-pulse">
                <CardHeader>
                  <div className="h-6 w-3/4 rounded bg-muted" />
                  <div className="mt-2 h-4 w-1/2 rounded bg-muted" />
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="h-4 w-full rounded bg-muted" />
                    <div className="h-4 w-2/3 rounded bg-muted" />
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>
    );
  }

  if (error || !data) {
    return null;
  }

  return (
    <section className="py-16">
      <div className="container">
        <div className="mb-8 text-center">
          <h2 className="mb-3 text-3xl font-bold">Featured Jobs</h2>
          <p className="text-muted-foreground">
            Latest opportunities in the UN system
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {data.jobs.map((job) => {
            const daysLeft = job.deadline
              ? getDaysUntilDeadline(job.deadline)
              : null;

            return (
              <Card
                key={job.id}
                className="transition-shadow hover:shadow-lg"
              >
                <CardHeader>
                  <div className="mb-2 flex items-start justify-between">
                    <div className="rounded-lg bg-primary/10 p-2">
                      <Briefcase className="h-5 w-5 text-primary" />
                    </div>
                    {daysLeft !== null && (
                      <span
                        className={`rounded-full px-2 py-1 text-xs font-medium ${
                          daysLeft <= 7
                            ? "bg-destructive/10 text-destructive"
                            : "bg-primary/10 text-primary"
                        }`}
                      >
                        {daysLeft}d left
                      </span>
                    )}
                  </div>
                  <CardTitle className="line-clamp-2 text-lg">
                    {job.title}
                  </CardTitle>
                  <p className="text-sm font-medium text-primary">
                    {job.organization}
                  </p>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 text-sm text-muted-foreground">
                    {job.location && (
                      <div className="flex items-center gap-2">
                        <MapPin className="h-4 w-4" />
                        <span className="line-clamp-1">{job.location}</span>
                      </div>
                    )}
                    {job.grade && (
                      <div className="flex items-center gap-2">
                        <Briefcase className="h-4 w-4" />
                        <span>Grade: {job.grade}</span>
                      </div>
                    )}
                    {job.deadline && (
                      <div className="flex items-center gap-2">
                        <Calendar className="h-4 w-4" />
                        <span>Deadline: {formatDate(job.deadline)}</span>
                      </div>
                    )}
                  </div>
                  <Button
                    variant="link"
                    className="mt-4 h-auto p-0"
                    asChild
                  >
                    <Link href={`/jobs/${job.id}`}>
                      View Details
                      <ArrowRight className="ml-2 h-4 w-4" />
                    </Link>
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>

        <div className="mt-8 text-center">
          <Button size="lg" asChild>
            <Link href="/jobs">Browse All Jobs</Link>
          </Button>
        </div>
      </div>
    </section>
  );
}



