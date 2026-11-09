 import SideBar from "@/Components/SidBar/SideBar";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen">
      <SideBar />
     <main className="  sm:ml-64  ">
          {children}
        </main>
    </div>
  );
}