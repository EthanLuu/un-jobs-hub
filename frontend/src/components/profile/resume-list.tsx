"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { FileText, CheckCircle, Briefcase, Trash2 } from "lucide-react";
import { formatDate } from "@/lib/utils";

interface Resume {
  id: number;
  filename: string;
  is_active: boolean;
  created_at: string;
  skills?: string[];
  experience_years?: number;
}

interface ResumeListProps {
  resumes: Resume[];
  onDelete: (resumeId: number) => void;
}

export function ResumeList({ resumes, onDelete }: ResumeListProps) {
  if (resumes.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>My Resumes</CardTitle>
          <CardDescription>
            Manage your uploaded resumes
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="py-8 text-center">
            <FileText className="mx-auto mb-4 h-12 w-12 text-muted-foreground" />
            <p className="text-muted-foreground">
              No resumes uploaded yet. Upload your first resume to get started!
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>My Resumes</CardTitle>
        <CardDescription>
          Manage your uploaded resumes
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {resumes.map((resume) => (
            <div
              key={resume.id}
              className="flex items-center justify-between rounded-lg border p-4"
            >
              <div className="flex items-start gap-4">
                <div className="rounded-lg bg-primary/10 p-3">
                  <FileText className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold">{resume.filename}</h3>
                    {resume.is_active && (
                      <Badge variant="default">
                        <CheckCircle className="mr-1 h-3 w-3" />
                        Active
                      </Badge>
                    )}
                  </div>
                  <p className="mt-1 text-sm text-muted-foreground">
                    Uploaded {formatDate(resume.created_at)}
                  </p>
                  {resume.skills && resume.skills.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1">
                      {resume.skills.slice(0, 5).map((skill: string) => (
                        <Badge key={skill} variant="outline">
                          {skill}
                        </Badge>
                      ))}
                      {resume.skills.length > 5 && (
                        <Badge variant="outline">
                          +{resume.skills.length - 5} more
                        </Badge>
                      )}
                    </div>
                  )}
                  {resume.experience_years && (
                    <div className="mt-2 flex items-center gap-1 text-sm text-muted-foreground">
                      <Briefcase className="h-4 w-4" />
                      <span>{resume.experience_years} years experience</span>
                    </div>
                  )}
                </div>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => onDelete(resume.id)}
              >
                <Trash2 className="h-4 w-4 text-destructive" />
              </Button>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
