import { Hero } from "@/components/home/hero";
import { FeaturedJobs } from "@/components/home/featured-jobs";
import { Features } from "@/components/home/features";
import { Stats } from "@/components/home/stats";

export default function Home() {
  return (
    <div className="flex flex-col">
      <Hero />
      <Stats />
      <FeaturedJobs />
      <Features />
    </div>
  );
}



