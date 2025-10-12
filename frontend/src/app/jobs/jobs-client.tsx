"use client";

import { useState } from "react";
import useSWR from "swr";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import { Search, Filter, MapPin, Calendar, Briefcase } from "lucide-react";
import Link from "next/link";
import { formatDate, getDaysUntilDeadline } from "@/lib/utils";

export function JobsClient() {
  const [page, setPage] = useState(1);
  const [keywords, setKeywords] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [organization, setOrganization] = useState("");

  const params: Record<string, string | number> = { page, page_size: 20 };
  if (searchTerm) params.keywords = searchTerm;
  if (organization) params.organization = organization;

  const { data, error, isLoading } = useSWR(
    JSON.stringify(params),
    () => api.getJobs(params)
  );

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setSearchTerm(keywords);
    setPage(1);
  };

  return (
    <div className="container py-8">
      <div className="mb-8">
        <h1 className="mb-4 text-4xl font-bold">Browse UN Jobs</h1>
        <p className="text-muted-foreground">
          Search through thousands of opportunities in the UN system
        </p>
      </div>

      {/* Search and Filters */}
      <div className="mb-8 rounded-lg border bg-card p-6">
        <form onSubmit={handleSearch} className="mb-4 flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
            <Input
              type="text"
              placeholder="Search by job title, keyword..."
              className="pl-10"
              value={keywords}
              onChange={(e) => setKeywords(e.target.value)}
            />
          </div>
          <Button type="submit">Search</Button>
        </form>

        <div className="flex gap-2">
          <Button
            variant={organization === "" ? "default" : "outline"}
            size="sm"
            onClick={() => {
              setOrganization("");
              setPage(1);
            }}
          >
            All
          </Button>
          {["UN", "UNDP", "UNICEF", "WHO", "FAO", "UNOPS"].map((org) => (
            <Button
              key={org}
              variant={organization === org ? "default" : "outline"}
              size="sm"
              onClick={() => {
                setOrganization(org);
                setPage(1);
              }}
            >
              {org}
            </Button>
          ))}
        </div>
      </div>

      {/* Results */}
      {isLoading ? (
        <div className="space-y-4">
          {[...Array(10)].map((_, i) => (
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
      ) : error || !data ? (
        <Card>
          <CardContent className="py-8 text-center">
            <p className="text-muted-foreground">
              Failed to load jobs. Please try again later.
            </p>
          </CardContent>
        </Card>
      ) : data.jobs.length === 0 ? (
        <Card>
          <CardContent className="py-8 text-center">
            <p className="text-muted-foreground">
              No jobs found. Try adjusting your search criteria.
            </p>
          </CardContent>
        </Card>
      ) : (
        <>
          <div className="mb-4 flex items-center justify-between">
            <p className="text-sm text-muted-foreground">
              Showing {(page - 1) * 20 + 1} -{" "}
              {Math.min(page * 20, data.total)} of {data.total} jobs
            </p>
          </div>

          <div className="space-y-4">
            {data.jobs.map((job) => {
              const daysLeft = job.deadline
                ? getDaysUntilDeadline(job.deadline)
                : null;

              return (
                <Card
                  key={job.id}
                  className="transition-shadow hover:shadow-md"
                >
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <CardTitle className="mb-2">
                          <Link
                            href={`/jobs/${job.id}`}
                            className="hover:text-primary"
                          >
                            {job.title}
                          </Link>
                        </CardTitle>
                        <p className="text-sm font-medium text-primary">
                          {job.organization}
                        </p>
                      </div>
                      {daysLeft !== null && (
                        <span
                          className={`rounded-full px-3 py-1 text-xs font-medium ${
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
                    <p className="mb-4 line-clamp-2 text-sm text-muted-foreground">
                      {job.description}
                    </p>
                    <div className="flex flex-wrap gap-4 text-sm">
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
                  </CardContent>
                </Card>
              );
            })}
          </div>

          {/* Pagination */}
          {data.total_pages > 1 && (
            <div className="mt-8 flex justify-center gap-2">
              <Button
                variant="outline"
                disabled={page === 1}
                onClick={() => setPage(page - 1)}
              >
                Previous
              </Button>
              <div className="flex items-center gap-2">
                <span className="text-sm text-muted-foreground">
                  Page {page} of {data.total_pages}
                </span>
              </div>
              <Button
                variant="outline"
                disabled={page === data.total_pages}
                onClick={() => setPage(page + 1)}
              >
                Next
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}



