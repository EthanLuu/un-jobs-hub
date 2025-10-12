"use client";

import { Users, Briefcase, Building2, TrendingUp } from "lucide-react";

const stats = [
  {
    icon: Briefcase,
    value: "5000+",
    label: "Active Jobs",
  },
  {
    icon: Building2,
    value: "30+",
    label: "UN Organizations",
  },
  {
    icon: Users,
    value: "10000+",
    label: "Job Seekers",
  },
  {
    icon: TrendingUp,
    value: "95%",
    label: "Success Rate",
  },
];

export function Stats() {
  return (
    <section className="border-y bg-muted/50 py-12">
      <div className="container">
        <div className="grid grid-cols-2 gap-8 md:grid-cols-4">
          {stats.map((stat, index) => (
            <div key={index} className="text-center">
              <div className="mb-3 inline-flex items-center justify-center">
                <stat.icon className="h-8 w-8 text-primary" />
              </div>
              <div className="mb-1 text-3xl font-bold">{stat.value}</div>
              <div className="text-sm text-muted-foreground">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}



