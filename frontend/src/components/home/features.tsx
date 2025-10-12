import {
  Search,
  Heart,
  FileText,
  Sparkles,
  Bell,
  Globe,
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

const features = [
  {
    icon: Search,
    title: "Smart Job Search",
    description:
      "Advanced filters to find jobs by organization, location, grade, and category across the entire UN system.",
  },
  {
    icon: Sparkles,
    title: "AI-Powered Matching",
    description:
      "Upload your resume and get intelligent job recommendations based on your skills and experience.",
  },
  {
    icon: FileText,
    title: "Resume Analysis",
    description:
      "Get instant feedback on your resume and see how well you match each position.",
  },
  {
    icon: Heart,
    title: "Save Favorites",
    description:
      "Bookmark jobs you're interested in and track your application status all in one place.",
  },
  {
    icon: Bell,
    title: "Job Alerts",
    description:
      "Set up custom alerts and get notified when new jobs matching your criteria are posted.",
  },
  {
    icon: Globe,
    title: "Global Coverage",
    description:
      "Access jobs from 30+ UN organizations including UNDP, UNICEF, WHO, FAO, and more.",
  },
];

export function Features() {
  return (
    <section className="bg-muted/50 py-16">
      <div className="container">
        <div className="mb-12 text-center">
          <h2 className="mb-3 text-3xl font-bold">
            Everything You Need for Your UN Career
          </h2>
          <p className="mx-auto max-w-2xl text-muted-foreground">
            Our platform provides all the tools and features you need to find
            and land your dream job in the United Nations system.
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {features.map((feature, index) => (
            <Card key={index} className="border-2 transition-colors hover:border-primary">
              <CardContent className="pt-6">
                <div className="mb-4 inline-flex rounded-lg bg-primary/10 p-3">
                  <feature.icon className="h-6 w-6 text-primary" />
                </div>
                <h3 className="mb-2 text-xl font-semibold">{feature.title}</h3>
                <p className="text-muted-foreground">{feature.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}



