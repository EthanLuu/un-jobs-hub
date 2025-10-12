"use client";

import { useState } from "react";
import useSWR from "swr";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";
import { User, FileText, Upload, Trash2, CheckCircle, Clock, Briefcase } from "lucide-react";
import { formatDate } from "@/lib/utils";

export function ProfileClient() {
  const [isEditingProfile, setIsEditingProfile] = useState(false);
  const [fullName, setFullName] = useState("");
  const [username, setUsername] = useState("");
  const [uploadingResume, setUploadingResume] = useState(false);

  const { data: user, mutate: mutateUser } = useSWR(
    "user",
    async () => {
      try {
        return await api.getCurrentUser();
      } catch (error) {
        return null;
      }
    }
  );

  const { data: resumes, mutate: mutateResumes } = useSWR(
    "resumes",
    async () => {
      try {
        return await api.getResumes();
      } catch (error) {
        return [];
      }
    }
  );

  const handleProfileUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.updateProfile({
        full_name: fullName || undefined,
        username: username || undefined,
      });
      mutateUser();
      setIsEditingProfile(false);
    } catch (error) {
      console.error("Failed to update profile:", error);
      alert("Failed to update profile");
    }
  };

  const handleResumeUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploadingResume(true);
    try {
      await api.uploadResume(file);
      mutateResumes();
      alert("Resume uploaded successfully!");
    } catch (error) {
      console.error("Failed to upload resume:", error);
      alert("Failed to upload resume");
    } finally {
      setUploadingResume(false);
      e.target.value = "";
    }
  };

  const handleResumeDelete = async (resumeId: number) => {
    if (!confirm("Are you sure you want to delete this resume?")) return;

    try {
      await api.deleteResume(resumeId);
      mutateResumes();
    } catch (error) {
      console.error("Failed to delete resume:", error);
      alert("Failed to delete resume");
    }
  };

  if (!user) {
    return (
      <div className="container py-8">
        <Card>
          <CardContent className="py-12 text-center">
            <User className="mx-auto mb-4 h-16 w-16 text-muted-foreground" />
            <h2 className="mb-2 text-xl font-semibold">Please Log In</h2>
            <p className="mb-6 text-muted-foreground">
              You need to be logged in to view your profile
            </p>
            <Button asChild>
              <a href="/login">Log In</a>
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!resumes) {
    return (
      <div className="container py-8">
        <Card>
          <CardContent className="py-8 text-center">
            <p className="text-muted-foreground">Loading...</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container py-8">
      <div className="mb-8">
        <h1 className="mb-2 text-4xl font-bold">My Profile</h1>
        <p className="text-muted-foreground">
          Manage your account and resume information
        </p>
      </div>

      <Tabs defaultValue="profile" className="space-y-6">
        <TabsList>
          <TabsTrigger value="profile">
            <User className="mr-2 h-4 w-4" />
            Profile
          </TabsTrigger>
          <TabsTrigger value="resumes">
            <FileText className="mr-2 h-4 w-4" />
            Resumes
          </TabsTrigger>
        </TabsList>

        <TabsContent value="profile">
          <Card>
            <CardHeader>
              <CardTitle>Profile Information</CardTitle>
              <CardDescription>
                Update your account details and personal information
              </CardDescription>
            </CardHeader>
            <CardContent>
              {!isEditingProfile ? (
                <div className="space-y-4">
                  <div>
                    <Label className="text-muted-foreground">Email</Label>
                    <p className="mt-1 font-medium">{user.email}</p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Username</Label>
                    <p className="mt-1 font-medium">{user.username}</p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Full Name</Label>
                    <p className="mt-1 font-medium">{user.full_name || "Not set"}</p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Member Since</Label>
                    <p className="mt-1 font-medium">{formatDate(user.created_at)}</p>
                  </div>
                  <Button onClick={() => {
                    setFullName(user.full_name || "");
                    setUsername(user.username);
                    setIsEditingProfile(true);
                  }}>
                    Edit Profile
                  </Button>
                </div>
              ) : (
                <form onSubmit={handleProfileUpdate} className="space-y-4">
                  <div>
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      type="email"
                      value={user.email}
                      disabled
                      className="mt-1"
                    />
                  </div>
                  <div>
                    <Label htmlFor="username">Username</Label>
                    <Input
                      id="username"
                      type="text"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      className="mt-1"
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="fullName">Full Name</Label>
                    <Input
                      id="fullName"
                      type="text"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      className="mt-1"
                    />
                  </div>
                  <div className="flex gap-2">
                    <Button type="submit">Save Changes</Button>
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => setIsEditingProfile(false)}
                    >
                      Cancel
                    </Button>
                  </div>
                </form>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="resumes">
          <div className="space-y-6">
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
                    onChange={handleResumeUpload}
                    disabled={uploadingResume}
                    className="hidden"
                  />
                  <Button
                    onClick={() => document.getElementById("resume-upload")?.click()}
                    disabled={uploadingResume}
                  >
                    <Upload className="mr-2 h-4 w-4" />
                    {uploadingResume ? "Uploading..." : "Upload Resume"}
                  </Button>
                  <p className="text-sm text-muted-foreground">
                    Accepted formats: PDF, DOCX (Max 10MB)
                  </p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>My Resumes</CardTitle>
                <CardDescription>
                  Manage your uploaded resumes
                </CardDescription>
              </CardHeader>
              <CardContent>
                {resumes.length === 0 ? (
                  <div className="py-8 text-center">
                    <FileText className="mx-auto mb-4 h-12 w-12 text-muted-foreground" />
                    <p className="text-muted-foreground">
                      No resumes uploaded yet. Upload your first resume to get started!
                    </p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {resumes.map((resume: any) => (
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
                          onClick={() => handleResumeDelete(resume.id)}
                        >
                          <Trash2 className="h-4 w-4 text-destructive" />
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}

