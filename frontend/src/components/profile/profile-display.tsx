"use client";

import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { formatDate } from "@/lib/utils";

interface User {
  email: string;
  username: string;
  full_name?: string;
  created_at: string;
}

interface ProfileDisplayProps {
  user: User;
  onEdit: () => void;
}

export function ProfileDisplay({ user, onEdit }: ProfileDisplayProps) {
  return (
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
      <Button onClick={onEdit}>
        Edit Profile
      </Button>
    </div>
  );
}
