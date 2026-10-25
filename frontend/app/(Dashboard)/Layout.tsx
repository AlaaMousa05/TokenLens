 import SideBar from "@/Components/SidBar/SideBar";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen">
      <SideBar />
      <main className="min-w-0 flex-1">{children}</main>
    </div>
  );
}