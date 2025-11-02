"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Search } from "lucide-react";

export function Hero() {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState("");

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      router.push(`/jobs?keywords=${encodeURIComponent(searchQuery)}`);
    } else {
      router.push("/jobs");
    }
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2,
        delayChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.5,
        ease: "easeOut",
      },
    },
  };

  return (
    <section className="relative overflow-hidden bg-gradient-to-b from-primary/10 via-primary/5 to-background py-20 md:py-32">
      <div className="container relative z-10">
        <motion.div
          className="mx-auto max-w-3xl text-center"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          <motion.h1
            className="mb-6 text-4xl font-bold tracking-tight sm:text-5xl md:text-6xl"
            variants={itemVariants}
          >
            Find Your Dream Job in the{" "}
            <span className="text-primary bg-clip-text">UN System</span>
          </motion.h1>
          <motion.p
            className="mb-8 text-lg text-muted-foreground md:text-xl"
            variants={itemVariants}
          >
            Search and apply to thousands of positions across UN, UNDP, UNICEF,
            WHO, FAO, and more. Get AI-powered job matching and personalized
            recommendations.
          </motion.p>

          <motion.form
            onSubmit={handleSearch}
            className="mx-auto flex max-w-2xl gap-2"
            variants={itemVariants}
          >
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
              <Input
                type="text"
                placeholder="Search by job title, keyword, or location..."
                className="h-12 pl-10 pr-4"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <Button type="submit" size="lg" className="h-12">
              Search Jobs
            </Button>
          </motion.form>

          <motion.div
            className="mt-8 flex flex-wrap items-center justify-center gap-4 text-sm text-muted-foreground"
            variants={itemVariants}
          >
            <span>Popular searches:</span>
            <Button
              variant="link"
              className="h-auto p-0 text-sm"
              onClick={() => {
                setSearchQuery("Programme Management");
                handleSearch(new Event("submit") as any);
              }}
            >
              Programme Management
            </Button>
            <Button
              variant="link"
              className="h-auto p-0 text-sm"
              onClick={() => {
                setSearchQuery("Human Rights");
                handleSearch(new Event("submit") as any);
              }}
            >
              Human Rights
            </Button>
            <Button
              variant="link"
              className="h-auto p-0 text-sm"
              onClick={() => {
                setSearchQuery("Finance");
                handleSearch(new Event("submit") as any);
              }}
            >
              Finance
            </Button>
          </motion.div>
        </motion.div>
      </div>

      {/* Decorative elements */}
      <div className="absolute inset-0 -z-10 opacity-20">
        <motion.div
          className="absolute left-1/2 top-0 h-96 w-96 -translate-x-1/2 -translate-y-1/2 rounded-full bg-primary blur-3xl"
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.3, 0.5, 0.3],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
      </div>
    </section>
  );
}



