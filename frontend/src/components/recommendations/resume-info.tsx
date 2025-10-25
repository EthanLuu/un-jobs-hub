"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { FileText, Briefcase } from "lucide-react";

interface Resume {
  id: number;
  filename: string;
  is_active: boolean;
  skills?: string[];
  experience_years?: number;
}

interface ResumeInfoProps {
  resume: Resume;
}

export function ResumeInfo({ resume }: ResumeInfoProps) {
  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle className="text-lg">Analyzing Resume</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-center gap-4">
          <div className="rounded-lg bg-primary/10 p-3">
            <FileText className="h-6 w-6 text-primary" />
          </div>
          <div className="flex-1">
            <p className="font-medium">{resume.filename}</p>
            <div className="mt-1 flex flex-wrap gap-2">
              {resume.skills && resume.skills.length > 0 && (
                <>
                  {resume.skills.slice(0, 6).map((skill: string) => (
                    <Badge key={skill} variant="outline" className="text-xs">
                      {skill}
                    </Badge>
                  ))}
                  {resume.skills.length > 6 && (
                    <Badge variant="outline" className="text-xs">
                      +{resume.skills.length - 6} more
                    </Badge>
                  )}
                </>
              )}
            </div>
          </div>
          {resume.experience_years && (
            <div className="flex items-center gap-2 rounded-lg border px-4 py-2">
              <Briefcase className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="text-xs text-muted-foreground">Experience</p>
                <p className="font-semibold">{resume.experience_years} years</p>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
