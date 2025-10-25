import { Metadata } from "next";
import { Suspense } from "react";
import { JobsClient } from "./jobs-client";

export const metadata: Metadata = {
  title: "Browse Jobs | UNJobsHub",
  description: "Search and filter UN system jobs. Find your perfect position across UNDP, UNICEF, WHO, and more.",
};

export default function JobsPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <JobsClient />
    </Suspense>
  );
}



