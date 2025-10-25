"use client";

import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import useSWR from "swr";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";
import { Search, Filter, MapPin, Calendar, Briefcase, GraduationCap, TrendingUp, X, ChevronDown, Share2, ArrowUpDown } from "lucide-react";
import Link from "next/link";
import { formatDate, getDaysUntilDeadline } from "@/lib/utils";

export function JobsClient() {
  const router = useRouter();
  const searchParams = useSearchParams();

  // Initialize state from URL params
  const [page, setPage] = useState(parseInt(searchParams.get("page") || "1"));
  const [keywords, setKeywords] = useState(searchParams.get("q") || "");
  const [searchTerm, setSearchTerm] = useState(searchParams.get("q") || "");
  const [organization, setOrganization] = useState(searchParams.get("org") || "");
  const [category, setCategory] = useState(searchParams.get("cat") || "");
  const [grade, setGrade] = useState(searchParams.get("grade") || "");
  const [location, setLocation] = useState(searchParams.get("loc") || "");
  const [educationLevel, setEducationLevel] = useState(searchParams.get("edu") || "");
  const [minExperience, setMinExperience] = useState(searchParams.get("minExp") || "");
  const [maxExperience, setMaxExperience] = useState(searchParams.get("maxExp") || "");
  const [contractType, setContractType] = useState(searchParams.get("contract") || "");
  const [sortBy, setSortBy] = useState(searchParams.get("sort") || "created_at");
  const [sortOrder, setSortOrder] = useState(searchParams.get("order") || "desc");
  const [showFilters, setShowFilters] = useState(false);

  // Update URL when filters change
  useEffect(() => {
    const params = new URLSearchParams();
    if (page > 1) params.set("page", page.toString());
    if (searchTerm) params.set("q", searchTerm);
    if (organization) params.set("org", organization);
    if (category) params.set("cat", category);
    if (grade) params.set("grade", grade);
    if (location) params.set("loc", location);
    if (educationLevel) params.set("edu", educationLevel);
    if (minExperience) params.set("minExp", minExperience);
    if (maxExperience) params.set("maxExp", maxExperience);
    if (contractType) params.set("contract", contractType);
    if (sortBy !== "created_at") params.set("sort", sortBy);
    if (sortOrder !== "desc") params.set("order", sortOrder);

    const queryString = params.toString();
    const newUrl = queryString ? `/jobs?${queryString}` : "/jobs";
    router.replace(newUrl, { scroll: false });
  }, [page, searchTerm, organization, category, grade, location, educationLevel, minExperience, maxExperience, contractType, sortBy, sortOrder, router]);

  const params: Record<string, string | number> = {
    page,
    page_size: 20,
    sort_by: sortBy,
    sort_order: sortOrder
  };

  if (searchTerm) params.keywords = searchTerm;
  if (organization) params.organization = organization;
  if (category) params.category = category;
  if (grade) params.grade = grade;
  if (location) params.location = location;
  if (educationLevel) params.education_level = educationLevel;
  if (minExperience) params.min_experience = parseInt(minExperience);
  if (maxExperience) params.max_experience = parseInt(maxExperience);
  if (contractType) params.contract_type = contractType;

  const { data, error, isLoading } = useSWR(
    JSON.stringify(params),
    () => api.getJobs(params)
  );

  // Fetch filter options
  const { data: filterOptions } = useSWR("filter-options", () =>
    api.getFilterOptions()
  );

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setSearchTerm(keywords);
    setPage(1);
  };

  const clearFilters = () => {
    setSearchTerm("");
    setKeywords("");
    setOrganization("");
    setCategory("");
    setGrade("");
    setLocation("");
    setEducationLevel("");
    setMinExperience("");
    setMaxExperience("");
    setContractType("");
    setPage(1);
  };

  const shareSearch = async () => {
    const url = window.location.href;
    try {
      await navigator.clipboard.writeText(url);
      // You could add a toast notification here
      alert("搜索链接已复制到剪贴板！");
    } catch (err) {
      console.error("Failed to copy:", err);
    }
  };

  const activeFiltersCount = [organization, category, grade, location, educationLevel, minExperience, maxExperience, contractType].filter(Boolean).length;

  // Validate grade - should be in format like P-3, G-5, D-1, NO-A, etc.
  const isValidGrade = (grade: string | undefined): boolean => {
    if (!grade) return false;
    const gradePattern = /^(P-\d+|G-\d+|D-\d+|NO-[A-Z]|FS-\d+|L-\d+|GS-\d+|UG)$/i;
    return gradePattern.test(grade.trim());
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
        {/* Search Bar */}
        <form onSubmit={handleSearch} className="mb-4 flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
            <Input
              type="text"
              placeholder="Search by title, description, organization..."
              className="pl-10"
              value={keywords}
              onChange={(e) => setKeywords(e.target.value)}
            />
          </div>
          <Button type="submit">Search</Button>
          <Button
            type="button"
            variant="outline"
            onClick={() => setShowFilters(!showFilters)}
          >
            <Filter className="mr-2 h-4 w-4" />
            Filters
            {activeFiltersCount > 0 && (
              <Badge variant="secondary" className="ml-2">
                {activeFiltersCount}
              </Badge>
            )}
          </Button>
        </form>

        {/* Organization Quick Filters */}
        <div className="mb-4 flex flex-wrap items-center gap-2">
          <span className="text-xs font-medium text-muted-foreground">Quick filters:</span>
          <Button
            variant={organization === "" ? "default" : "outline"}
            size="sm"
            onClick={() => {
              setOrganization("");
              setPage(1);
            }}
          >
            All Organizations
          </Button>
          {filterOptions?.organizations?.slice(0, 6).map((org) => (
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

          {/* Quick Sort */}
          <div className="ml-auto flex items-center gap-2">
            <ArrowUpDown className="h-3 w-3 text-muted-foreground" />
            <select
              className="rounded-md border border-input bg-background px-2 py-1 text-xs"
              value={`${sortBy}-${sortOrder}`}
              onChange={(e) => {
                const [newSortBy, newSortOrder] = e.target.value.split("-");
                setSortBy(newSortBy);
                setSortOrder(newSortOrder);
              }}
            >
              <option value="created_at-desc">Newest First</option>
              <option value="created_at-asc">Oldest First</option>
              <option value="deadline-asc">Deadline (Soonest)</option>
              <option value="deadline-desc">Deadline (Latest)</option>
              <option value="title-asc">Title (A-Z)</option>
              <option value="title-desc">Title (Z-A)</option>
            </select>
          </div>
        </div>

        {/* Advanced Filters */}
        {showFilters && (
          <div className="space-y-4 border-t pt-4">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold">Advanced Filters</h3>
              {activeFiltersCount > 0 && (
                <Button variant="ghost" size="sm" onClick={clearFilters}>
                  <X className="mr-1 h-4 w-4" />
                  Clear All
                </Button>
              )}
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {/* Category Filter */}
              <div>
                <label className="mb-2 block text-sm font-medium">Category</label>
                <select
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={category}
                  onChange={(e) => {
                    setCategory(e.target.value);
                    setPage(1);
                  }}
                >
                  <option value="">All Categories</option>
                  {filterOptions?.categories?.map((cat) => (
                    <option key={cat} value={cat}>
                      {cat}
                    </option>
                  ))}
                </select>
              </div>

              {/* Grade Filter */}
              <div>
                <label className="mb-2 block text-sm font-medium">Grade</label>
                <select
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={grade}
                  onChange={(e) => {
                    setGrade(e.target.value);
                    setPage(1);
                  }}
                >
                  <option value="">All Grades</option>
                  {filterOptions?.grades?.map((g) => (
                    <option key={g} value={g}>
                      {g}
                    </option>
                  ))}
                </select>
              </div>

              {/* Location Filter */}
              <div>
                <label className="mb-2 block text-sm font-medium">Location</label>
                <Input
                  placeholder="e.g. Geneva, New York"
                  value={location}
                  onChange={(e) => {
                    setLocation(e.target.value);
                    setPage(1);
                  }}
                />
              </div>

              {/* Education Level Filter */}
              <div>
                <label className="mb-2 block text-sm font-medium">Education Level</label>
                <select
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={educationLevel}
                  onChange={(e) => {
                    setEducationLevel(e.target.value);
                    setPage(1);
                  }}
                >
                  <option value="">All Levels</option>
                  {filterOptions?.education_levels?.map((level) => (
                    <option key={level} value={level}>
                      {level}
                    </option>
                  ))}
                </select>
              </div>

              {/* Min Experience */}
              <div>
                <label className="mb-2 block text-sm font-medium">Min Experience (years)</label>
                <Input
                  type="number"
                  min="0"
                  placeholder="e.g. 3"
                  value={minExperience}
                  onChange={(e) => {
                    setMinExperience(e.target.value);
                    setPage(1);
                  }}
                />
              </div>

              {/* Max Experience */}
              <div>
                <label className="mb-2 block text-sm font-medium">Max Experience (years)</label>
                <Input
                  type="number"
                  min="0"
                  placeholder="e.g. 10"
                  value={maxExperience}
                  onChange={(e) => {
                    setMaxExperience(e.target.value);
                    setPage(1);
                  }}
                />
              </div>

              {/* Contract Type Filter */}
              <div>
                <label className="mb-2 block text-sm font-medium">Contract Type</label>
                <select
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={contractType}
                  onChange={(e) => {
                    setContractType(e.target.value);
                    setPage(1);
                  }}
                >
                  <option value="">All Types</option>
                  <option value="Fixed-term">Fixed-term</option>
                  <option value="Temporary">Temporary</option>
                  <option value="Consultant">Consultant</option>
                  <option value="Intern">Intern</option>
                  <option value="Staff">Staff</option>
                </select>
              </div>
            </div>

            {/* Sort Options */}
            <div className="border-t pt-4">
              <label className="mb-2 block text-sm font-medium">Sort By</label>
              <div className="flex gap-2">
                <select
                  className="rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                >
                  <option value="created_at">Date Added</option>
                  <option value="deadline">Deadline</option>
                  <option value="posted_date">Posted Date</option>
                  <option value="title">Title</option>
                </select>
                <select
                  className="rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={sortOrder}
                  onChange={(e) => setSortOrder(e.target.value)}
                >
                  <option value="desc">Descending</option>
                  <option value="asc">Ascending</option>
                </select>
              </div>
            </div>
          </div>
        )}
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
          {/* Results Summary */}
          <div className="mb-6 rounded-lg border bg-muted/50 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium">
                  Found {data.total.toLocaleString()} {data.total === 1 ? 'job' : 'jobs'}
                </p>
                <p className="text-xs text-muted-foreground">
                  Showing {(page - 1) * 20 + 1} - {Math.min(page * 20, data.total)} on page {page} of {data.total_pages}
                </p>
              </div>
              <div className="flex items-center gap-2">
                {(searchTerm || activeFiltersCount > 0) && (
                  <>
                    <Badge variant="secondary" className="text-xs">
                      {activeFiltersCount + (searchTerm ? 1 : 0)} active filter{(activeFiltersCount + (searchTerm ? 1 : 0)) > 1 ? 's' : ''}
                    </Badge>
                    <Button variant="ghost" size="sm" onClick={clearFilters}>
                      <X className="mr-1 h-3 w-3" />
                      Clear all
                    </Button>
                  </>
                )}
                <Button variant="outline" size="sm" onClick={shareSearch}>
                  <Share2 className="mr-1 h-3 w-3" />
                  Share
                </Button>
              </div>
            </div>

            {/* Active Filters Display */}
            {(searchTerm || organization || category || grade || location || educationLevel || minExperience || maxExperience) && (
              <div className="mt-3 flex flex-wrap gap-2 border-t pt-3">
                {searchTerm && (
                  <Badge variant="outline" className="gap-1">
                    Search: {searchTerm}
                    <button
                      onClick={() => {
                        setSearchTerm("");
                        setKeywords("");
                        setPage(1);
                      }}
                      className="ml-1 hover:text-destructive"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                )}
                {organization && (
                  <Badge variant="outline" className="gap-1">
                    Org: {organization}
                    <button
                      onClick={() => {
                        setOrganization("");
                        setPage(1);
                      }}
                      className="ml-1 hover:text-destructive"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                )}
                {category && (
                  <Badge variant="outline" className="gap-1">
                    Category: {category}
                    <button
                      onClick={() => {
                        setCategory("");
                        setPage(1);
                      }}
                      className="ml-1 hover:text-destructive"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                )}
                {grade && (
                  <Badge variant="outline" className="gap-1">
                    Grade: {grade}
                    <button
                      onClick={() => {
                        setGrade("");
                        setPage(1);
                      }}
                      className="ml-1 hover:text-destructive"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                )}
                {location && (
                  <Badge variant="outline" className="gap-1">
                    Location: {location}
                    <button
                      onClick={() => {
                        setLocation("");
                        setPage(1);
                      }}
                      className="ml-1 hover:text-destructive"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                )}
                {educationLevel && (
                  <Badge variant="outline" className="gap-1">
                    Education: {educationLevel}
                    <button
                      onClick={() => {
                        setEducationLevel("");
                        setPage(1);
                      }}
                      className="ml-1 hover:text-destructive"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                )}
                {minExperience && (
                  <Badge variant="outline" className="gap-1">
                    Min Exp: {minExperience}y
                    <button
                      onClick={() => {
                        setMinExperience("");
                        setPage(1);
                      }}
                      className="ml-1 hover:text-destructive"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                )}
                {maxExperience && (
                  <Badge variant="outline" className="gap-1">
                    Max Exp: {maxExperience}y
                    <button
                      onClick={() => {
                        setMaxExperience("");
                        setPage(1);
                      }}
                      className="ml-1 hover:text-destructive"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                )}
                {contractType && (
                  <Badge variant="outline" className="gap-1">
                    Contract: {contractType}
                    <button
                      onClick={() => {
                        setContractType("");
                        setPage(1);
                      }}
                      className="ml-1 hover:text-destructive"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                )}
              </div>
            )}
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
                    <div className="flex flex-wrap gap-x-4 gap-y-2 text-sm">
                      {job.location && (
                        <div className="flex items-center gap-1 text-muted-foreground">
                          <MapPin className="h-4 w-4" />
                          <span>{job.location}</span>
                        </div>
                      )}
                      {isValidGrade(job.grade) && (
                        <div className="flex items-center gap-1 text-muted-foreground">
                          <Briefcase className="h-4 w-4" />
                          <span>{job.grade}</span>
                        </div>
                      )}
                      {job.contract_type && (
                        <div className="flex items-center gap-1 text-muted-foreground">
                          <Briefcase className="h-4 w-4" />
                          <span>{job.contract_type}</span>
                        </div>
                      )}
                      {job.education_level && (
                        <div className="flex items-center gap-1 text-muted-foreground">
                          <GraduationCap className="h-4 w-4" />
                          <span>{job.education_level}</span>
                        </div>
                      )}
                      {job.years_of_experience !== undefined && job.years_of_experience !== null && (
                        <div className="flex items-center gap-1 text-muted-foreground">
                          <TrendingUp className="h-4 w-4" />
                          <span>{job.years_of_experience}+ yrs</span>
                        </div>
                      )}
                      {job.deadline && (
                        <div className="flex items-center gap-1 text-muted-foreground">
                          <Calendar className="h-4 w-4" />
                          <span>{formatDate(job.deadline)}</span>
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



