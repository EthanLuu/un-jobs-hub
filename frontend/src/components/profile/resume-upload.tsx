"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Upload } from "lucide-react";

interface ResumeUploadProps {
  onUpload: (file: File) => Promise<void>;
  isUploading: boolean;
}

export function ResumeUpload({ onUpload, isUploading }: ResumeUploadProps) {
  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      await onUpload(file);
    } finally {
      e.target.value = "";
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Upload Resume</CardTitle>
        <CardDescription>
          Upload your resume to get personalized job recommendations
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex items-center gap-4">
          <Input
            id="resume-upload"
            type="file"
            accept=".pdf,.docx"
            onChange={handleFileChange}
            disabled={isUploading}
            className="hidden"
          />
          <Button
            onClick={() => document.getElementById("resume-upload")?.click()}
            disabled={isUploading}
          >
            <Upload className="mr-2 h-4 w-4" />
            {isUploading ? "Uploading..." : "Upload Resume"}
          </Button>
          <p className="text-sm text-muted-foreground">
            Accepted formats: PDF, DOCX (Max 10MB)
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
