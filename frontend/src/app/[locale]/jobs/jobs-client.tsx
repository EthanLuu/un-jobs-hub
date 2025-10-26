"use client";

import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import useSWR from "swr";
import { Card, CardContent } from "@/components/ui/card";
import { api } from "@/lib/api";
import { JobCard } from "@/components/jobs/job-card";
import { JobSearchFilters } from "@/components/jobs/job-search-filters";
import { ActiveFilters } from "@/components/jobs/active-filters";
import { ResultsSummary } from "@/components/jobs/results-summary";
import { Pagination } from "@/components/jobs/pagination";

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
  const [viewMode, setViewMode] = useState<"list" | "grid" | "masonry">("masonry");

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

  const handleRemoveFilter = (filterType: string) => {
    switch (filterType) {
      case "search":
        setSearchTerm("");
        setKeywords("");
        break;
      case "organization":
        setOrganization("");
        break;
      case "category":
        setCategory("");
        break;
      case "grade":
        setGrade("");
        break;
      case "location":
        setLocation("");
        break;
      case "educationLevel":
        setEducationLevel("");
        break;
      case "minExperience":
        setMinExperience("");
        break;
      case "maxExperience":
        setMaxExperience("");
        break;
      case "contractType":
        setContractType("");
        break;
    }
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
      <JobSearchFilters
        searchTerm={searchTerm}
        setSearchTerm={setSearchTerm}
        keywords={keywords}
        setKeywords={setKeywords}
        organization={organization}
        setOrganization={setOrganization}
        category={category}
        setCategory={setCategory}
        grade={grade}
        setGrade={setGrade}
        location={location}
        setLocation={setLocation}
        educationLevel={educationLevel}
        setEducationLevel={setEducationLevel}
        minExperience={minExperience}
        setMinExperience={setMinExperience}
        maxExperience={maxExperience}
        setMaxExperience={setMaxExperience}
        contractType={contractType}
        setContractType={setContractType}
        sortBy={sortBy}
        setSortBy={setSortBy}
        sortOrder={sortOrder}
        setSortOrder={setSortOrder}
        showFilters={showFilters}
        setShowFilters={setShowFilters}
        filterOptions={filterOptions}
        onSearch={handleSearch}
        onClearFilters={clearFilters}
      />

      {/* Results */}
      {isLoading ? (
        <div className="space-y-4">
          {[...Array(10)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="p-6">
                <div className="space-y-2">
                  <div className="h-6 w-3/4 rounded bg-muted" />
                  <div className="mt-2 h-4 w-1/2 rounded bg-muted" />
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
          <ResultsSummary
            total={data.total}
            currentPage={page}
            pageSize={20}
            totalPages={data.total_pages}
            viewMode={viewMode}
            onViewModeChange={(mode: "list" | "grid" | "masonry") => setViewMode(mode)}
            activeFiltersCount={activeFiltersCount}
            hasSearchTerm={!!searchTerm}
            onClearFilters={clearFilters}
            onShare={shareSearch}
          />

          {/* Active Filters */}
          <ActiveFilters
            searchTerm={searchTerm}
            organization={organization}
            category={category}
            grade={grade}
            location={location}
            educationLevel={educationLevel}
            minExperience={minExperience}
            maxExperience={maxExperience}
            contractType={contractType}
            onRemoveFilter={handleRemoveFilter}
            onClearAll={clearFilters}
            onShare={shareSearch}
          />

          <div className={
            viewMode === "masonry" 
              ? "masonry" 
              : viewMode === "grid" 
                ? "grid gap-6 md:grid-cols-2 lg:grid-cols-3" 
                : "space-y-4"
          }>
            {data.jobs.map((job) => (
              <div key={job.id} className={viewMode === "masonry" ? "masonry-item" : ""}>
                <JobCard job={job} viewMode={viewMode as "list" | "grid" | "masonry"} />
              </div>
            ))}
          </div>

          {/* Pagination */}
          <Pagination
            currentPage={page}
            totalPages={data.total_pages}
            onPageChange={setPage}
          />
        </>
      )}
    </div>
  );
}



