"use client";

import { useState } from "react";
import useSWR from "swr";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { api } from "@/lib/api";
import { User, FileText } from "lucide-react";
import { ProfileDisplay } from "@/components/profile/profile-display";
import { ProfileEditForm } from "@/components/profile/profile-edit-form";
import { ResumeUpload } from "@/components/profile/resume-upload";
import { ResumeList } from "@/components/profile/resume-list";

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

  const handleProfileUpdate = async (data: { full_name?: string; username: string }) => {
    try {
      await api.updateProfile({
        full_name: data.full_name || undefined,
        username: data.username || undefined,
      });
      mutateUser();
      setIsEditingProfile(false);
    } catch (error) {
      console.error("Failed to update profile:", error);
      alert("Failed to update profile");
    }
  };

  const handleResumeUpload = async (file: File) => {
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
                <ProfileDisplay
                  user={user}
                  onEdit={() => {
                    setFullName(user.full_name || "");
                    setUsername(user.username);
                    setIsEditingProfile(true);
                  }}
                />
              ) : (
                <ProfileEditForm
                  user={user}
                  onSave={handleProfileUpdate}
                  onCancel={() => setIsEditingProfile(false)}
                />
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="resumes">
          <div className="space-y-6">
            <ResumeUpload
              onUpload={handleResumeUpload}
              isUploading={uploadingResume}
            />
            <ResumeList
              resumes={resumes}
              onDelete={handleResumeDelete}
            />
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}

