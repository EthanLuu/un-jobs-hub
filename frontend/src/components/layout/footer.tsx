import Link from "next/link";
import { Globe } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t bg-background">
      <div className="container py-8 md:py-12">
        <div className="grid grid-cols-1 gap-8 md:grid-cols-4">
          <div className="space-y-3">
            <div className="flex items-center space-x-2">
              <Globe className="h-6 w-6 text-primary" />
              <span className="text-lg font-bold">UNJobsHub</span>
            </div>
            <p className="text-sm text-muted-foreground">
              Your gateway to United Nations careers. Find and apply to jobs
              across the UN system.
            </p>
          </div>

          <div>
            <h3 className="mb-4 text-sm font-semibold">Organizations</h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>UN Secretariat</li>
              <li>UNDP</li>
              <li>UNICEF</li>
              <li>WHO</li>
              <li>FAO</li>
            </ul>
          </div>

          <div>
            <h3 className="mb-4 text-sm font-semibold">Resources</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/jobs" className="hover:text-primary">
                  Browse Jobs
                </Link>
              </li>
              <li>
                <Link href="/recommendations" className="hover:text-primary">
                  AI Recommendations
                </Link>
              </li>
              <li>
                <Link href="/profile" className="hover:text-primary">
                  My Profile
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <h3 className="mb-4 text-sm font-semibold">Company</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/about" className="hover:text-primary">
                  About Us
                </Link>
              </li>
              <li>
                <Link href="/contact" className="hover:text-primary">
                  Contact
                </Link>
              </li>
              <li>
                <Link href="/privacy" className="hover:text-primary">
                  Privacy Policy
                </Link>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-8 border-t pt-8 text-center text-sm text-muted-foreground">
          <p>&copy; 2025 UNJobsHub. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}



