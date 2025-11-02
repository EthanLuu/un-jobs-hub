import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

interface JobCardSkeletonProps {
  viewMode?: "list" | "grid" | "masonry";
}

export function JobCardSkeleton({ viewMode = "list" }: JobCardSkeletonProps) {
  const isCardMode = viewMode === "grid" || viewMode === "masonry";

  return (
    <Card className={viewMode === "masonry" ? "masonry-card" : ""}>
      <CardHeader>
        <div className={`flex items-start justify-between ${isCardMode ? "flex-col gap-2" : ""}`}>
          <div className="flex-1 space-y-2 w-full">
            <Skeleton className="h-6 w-3/4" />
            <Skeleton className="h-4 w-1/3" />
          </div>
          <Skeleton className="h-6 w-16 rounded-full" />
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="space-y-2">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-5/6" />
          </div>
          <div className={`flex flex-wrap gap-4 ${isCardMode ? "flex-col" : ""}`}>
            <Skeleton className="h-4 w-24" />
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-4 w-28" />
            <Skeleton className="h-4 w-16" />
          </div>
          {isCardMode && (
            <div className="pt-4 border-t">
              <Skeleton className="h-9 w-full" />
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
