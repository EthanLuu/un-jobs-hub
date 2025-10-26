"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { X, Share2 } from "lucide-react";

interface ActiveFiltersProps {
  searchTerm: string;
  organization: string;
  category: string;
  grade: string;
  location: string;
  educationLevel: string;
  minExperience: string;
  maxExperience: string;
  selectedContractTypes: string[];
  excludedContractTypes: string[];
  onRemoveFilter: (filterType: string) => void;
  onClearAll: () => void;
  onShare: () => void;
}

export function ActiveFilters({
  searchTerm,
  organization,
  category,
  grade,
  location,
  educationLevel,
  minExperience,
  maxExperience,
  selectedContractTypes,
  excludedContractTypes,
  onRemoveFilter,
  onClearAll,
  onShare,
}: ActiveFiltersProps) {
  const activeFiltersCount = [organization, category, grade, location, educationLevel, minExperience, maxExperience].filter(Boolean).length + selectedContractTypes.length + excludedContractTypes.length;

  return (
    <div className="mb-6 rounded-lg border bg-muted/50 p-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium">
            Found results with active filters
          </p>
          <p className="text-xs text-muted-foreground">
            {activeFiltersCount + (searchTerm ? 1 : 0)} active filter{(activeFiltersCount + (searchTerm ? 1 : 0)) > 1 ? 's' : ''}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {(searchTerm || activeFiltersCount > 0) && (
            <>
              <Badge variant="secondary" className="text-xs">
                {activeFiltersCount + (searchTerm ? 1 : 0)} active filter{(activeFiltersCount + (searchTerm ? 1 : 0)) > 1 ? 's' : ''}
              </Badge>
              <Button variant="ghost" size="sm" onClick={onClearAll}>
                <X className="mr-1 h-3 w-3" />
                Clear all
              </Button>
            </>
          )}
          <Button variant="outline" size="sm" onClick={onShare}>
            <Share2 className="mr-1 h-3 w-3" />
            Share
          </Button>
        </div>
      </div>

      {/* Active Filters Display */}
      {(searchTerm || organization || category || grade || location || educationLevel || minExperience || maxExperience || selectedContractTypes.length > 0 || excludedContractTypes.length > 0) && (
        <div className="mt-3 flex flex-wrap gap-2 border-t pt-3">
          {searchTerm && (
            <Badge variant="outline" className="gap-1">
              Search: {searchTerm}
              <button
                onClick={() => onRemoveFilter("search")}
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
                onClick={() => onRemoveFilter("organization")}
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
                onClick={() => onRemoveFilter("category")}
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
                onClick={() => onRemoveFilter("grade")}
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
                onClick={() => onRemoveFilter("location")}
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
                onClick={() => onRemoveFilter("educationLevel")}
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
                onClick={() => onRemoveFilter("minExperience")}
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
                onClick={() => onRemoveFilter("maxExperience")}
                className="ml-1 hover:text-destructive"
              >
                <X className="h-3 w-3" />
              </button>
            </Badge>
          )}
          {selectedContractTypes.length > 0 && (
            <Badge variant="outline" className="gap-1">
              Contract (Including): {selectedContractTypes.join(", ")}
              <button
                onClick={() => onRemoveFilter("contractType")}
                className="ml-1 hover:text-destructive"
              >
                <X className="h-3 w-3" />
              </button>
            </Badge>
          )}
          {excludedContractTypes.length > 0 && (
            <Badge variant="outline" className="gap-1 bg-destructive/10">
              Contract (Excluding): {excludedContractTypes.join(", ")}
              <button
                onClick={() => onRemoveFilter("contractType")}
                className="ml-1 hover:text-destructive"
              >
                <X className="h-3 w-3" />
              </button>
            </Badge>
          )}
        </div>
      )}
    </div>
  );
}
