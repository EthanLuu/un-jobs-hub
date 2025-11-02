"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Heart } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/use-toast";

interface BookmarkButtonProps {
  jobId: number;
  initialBookmarked?: boolean;
}

export function BookmarkButton({ jobId, initialBookmarked = false }: BookmarkButtonProps) {
  const [isBookmarked, setIsBookmarked] = useState(initialBookmarked);
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const handleToggleBookmark = async () => {
    setIsLoading(true);
    try {
      // TODO: Implement actual API call to bookmark/unbookmark job
      // For now, just simulate the action
      await new Promise(resolve => setTimeout(resolve, 500));

      setIsBookmarked(!isBookmarked);
      toast({
        title: isBookmarked ? "Bookmark removed" : "Job bookmarked",
        description: isBookmarked
          ? "Job removed from your favorites"
          : "Job added to your favorites",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update bookmark. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={handleToggleBookmark}
      disabled={isLoading}
      className="relative"
    >
      <motion.div
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
      >
        <Heart
          className={`h-5 w-5 transition-colors ${
            isBookmarked ? "fill-red-500 text-red-500" : "text-muted-foreground"
          }`}
        />
      </motion.div>
    </Button>
  );
}
