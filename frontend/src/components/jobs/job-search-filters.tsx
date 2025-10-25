"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Search, Filter, X, ArrowUpDown } from "lucide-react";

interface FilterOptions {
  organizations?: string[];
  categories?: string[];
  grades?: string[];
  education_levels?: string[];
}

interface JobSearchFiltersProps {
  searchTerm: string;
  setSearchTerm: (term: string) => void;
  keywords: string;
  setKeywords: (keywords: string) => void;
  organization: string;
  setOrganization: (org: string) => void;
  category: string;
  setCategory: (cat: string) => void;
  grade: string;
  setGrade: (grade: string) => void;
  location: string;
  setLocation: (loc: string) => void;
  educationLevel: string;
  setEducationLevel: (level: string) => void;
  minExperience: string;
  setMinExperience: (exp: string) => void;
  maxExperience: string;
  setMaxExperience: (exp: string) => void;
  contractType: string;
  setContractType: (type: string) => void;
  sortBy: string;
  setSortBy: (sort: string) => void;
  sortOrder: string;
  setSortOrder: (order: string) => void;
  showFilters: boolean;
  setShowFilters: (show: boolean) => void;
  filterOptions?: FilterOptions;
  onSearch: (e: React.FormEvent) => void;
  onClearFilters: () => void;
}

export function JobSearchFilters({
  searchTerm,
  setSearchTerm,
  keywords,
  setKeywords,
  organization,
  setOrganization,
  category,
  setCategory,
  grade,
  setGrade,
  location,
  setLocation,
  educationLevel,
  setEducationLevel,
  minExperience,
  setMinExperience,
  maxExperience,
  setMaxExperience,
  contractType,
  setContractType,
  sortBy,
  setSortBy,
  sortOrder,
  setSortOrder,
  showFilters,
  setShowFilters,
  filterOptions,
  onSearch,
  onClearFilters,
}: JobSearchFiltersProps) {
  const activeFiltersCount = [organization, category, grade, location, educationLevel, minExperience, maxExperience, contractType].filter(Boolean).length;

  return (
    <div className="mb-8 rounded-lg border bg-card p-6">
      {/* Search Bar */}
      <form onSubmit={onSearch} className="mb-4 flex gap-2">
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
              <Button variant="ghost" size="sm" onClick={onClearFilters}>
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
                onChange={(e) => setCategory(e.target.value)}
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
                onChange={(e) => setGrade(e.target.value)}
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
                onChange={(e) => setLocation(e.target.value)}
              />
            </div>

            {/* Education Level Filter */}
            <div>
              <label className="mb-2 block text-sm font-medium">Education Level</label>
              <select
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={educationLevel}
                onChange={(e) => setEducationLevel(e.target.value)}
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
                onChange={(e) => setMinExperience(e.target.value)}
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
                onChange={(e) => setMaxExperience(e.target.value)}
              />
            </div>

            {/* Contract Type Filter */}
            <div>
              <label className="mb-2 block text-sm font-medium">Contract Type</label>
              <select
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={contractType}
                onChange={(e) => setContractType(e.target.value)}
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
  );
}
