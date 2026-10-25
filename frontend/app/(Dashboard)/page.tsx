import React from 'react'
import StatsCards from "@/components/dashboard/StatsCards";
import RecentRunsTable from "@/components/dashboard/RecentRunsTable";
export default function page() {
 return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">Dashboard</h1>
      
      {/* عرض بطاقات الإحصائيات */}
      {/* <StatsCards /> */}
      
      {/* عرض جدول التشغيلات الأخيرة */}
      {/* <RecentRunsTable /> */}
    </div>
  );
}
