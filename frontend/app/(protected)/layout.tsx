
import AuthGuard from "@/Components/AuthGuard";
import SideBar from "@/Components/SidBar/SideBar";
 

export default function ProtectedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AuthGuard>
      <div className="flex min-h-screen">
        <SideBar />

        <main className="min-w-0 flex-1">
          {children}
        </main>
      </div>
    </AuthGuard>
  );
}
