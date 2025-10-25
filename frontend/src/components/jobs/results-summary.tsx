"use client";

import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Grid3x3, List, X } from "lucide-react";

interface ResultsSummaryProps {
  total: number;
  currentPage: number;
  pageSize: number;
  totalPages: number;
  viewMode: "list" | "grid";
  onViewModeChange: (mode: "list" | "grid") => void;
  activeFiltersCount: number;
  hasSearchTerm: boolean;
  onClearFilters: () => void;
  onShare: () => void;
}

export function ResultsSummary({
  total,
  currentPage,
  pageSize,
  totalPages,
  viewMode,
  onViewModeChange,
  activeFiltersCount,
  hasSearchTerm,
  onClearFilters,
  onShare,
}: ResultsSummaryProps) {
  const startItem = (currentPage - 1) * pageSize + 1;
  const endItem = Math.min(currentPage * pageSize, total);

  return (
    <div className="mb-6 rounded-lg border bg-muted/50 p-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium">
            Found {total.toLocaleString()} {total === 1 ? 'job' : 'jobs'}
          </p>
          <p className="text-xs text-muted-foreground">
            Showing {startItem} - {endItem} on page {currentPage} of {totalPages}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {/* View Mode Toggle */}
          <div className="flex items-center gap-1 rounded-md border">
            <Button
              variant={viewMode === "list" ? "default" : "ghost"}
              size="sm"
              onClick={() => onViewModeChange("list")}
              className="h-8"
            >
              <List className="h-4 w-4" />
            </Button>
            <Button
              variant={viewMode === "grid" ? "default" : "ghost"}
              size="sm"
              onClick={() => onViewModeChange("grid")}
              className="h-8"
            >
              <Grid3x3 className="h-4 w-4" />
            </Button>
          </div>
          {(hasSearchTerm || activeFiltersCount > 0) && (
            <>
              <Badge variant="secondary" className="text-xs">
                {activeFiltersCount + (hasSearchTerm ? 1 : 0)} active filter{(activeFiltersCount + (hasSearchTerm ? 1 : 0)) > 1 ? 's' : ''}
              </Badge>
              <Button variant="ghost" size="sm" onClick={onClearFilters}>
                <X className="mr-1 h-3 w-3" />
                Clear all
              </Button>
            </>
          )}
          <Button variant="outline" size="sm" onClick={onShare}>
            Share
          </Button>
        </div>
      </div>
    </div>
  );
}
