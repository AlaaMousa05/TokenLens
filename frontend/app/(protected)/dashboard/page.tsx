import RecentRunsTable from '@/Components/BasicTable/BasicTable';  
import StatsCards from '@/Components/StatsCards/StatsCards';
import React from 'react';
import Link from "next/link"; 
export default function Page() {
  return (
    <div className="min-h-screen bg-[#060b1f] text-white p-8">
     
      <div className="max-w-7xl mx-auto flex flex-col gap-6">
        
       
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-white ms-3  sm:text-xsm">Dashboard</h1>
            <p className="text-sm text-slate-400 mt-1">
              Overview of your recent runs and key metrics.
            </p>
          </div>
          
         
          <Link href="/newrun" className="bg-[#252fbb] hover:bg-[#6c73f5] text-white px-3 py-1.5 rounded-lg text-xs font-medium transition-colors 
          flex items-center gap-2 shadow-lg min-[800px]:max-[956px]:px-2 min-[800px]:max-[956px]:py-1 min-[800px]:max-[956px]:text-[11px] min-[800px]:max-[956px]:gap-1 ">
            + New Run
          </Link>
        </div>

        
        <div className="w-full">
          <StatsCards />
        </div>
        
        
        <div className="w-full">
          <RecentRunsTable />
        </div>

      </div>
    </div>
  );
}