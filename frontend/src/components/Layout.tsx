import { Outlet, Link, useLocation } from 'react-router-dom';
import type { NavItem } from '@/types';

const navigationItems: NavItem[] = [
  {
    title: 'Dashboard',
    href: '/dashboard',
  },
  {
    title: 'Asset Types',
    href: '/asset-types',
  },
  {
    title: 'Assets',
    href: '/assets',
  },
  {
    title: 'LLMs',
    href: '/llms',
  },
  {
    title: 'Prompts',
    href: '/prompts',
  },
  {
    title: 'Query Types',
    href: '/query-types',
  },
  {
    title: 'Schedules',
    href: '/schedules',
  },
  {
    title: 'Query Schedules',
    href: '/query-schedules',
  },
  {
    title: 'Surveys',
    href: '/surveys',
  },
  {
    title: 'Queries History',
    href: '/queries',
  },
  {
    title: 'Scheduled Queries',
    href: '/scheduled-queries',
  },
  {
    title: 'EventBridge Rules',
    href: '/eventbridge-rules',
  },
  {
    title: 'Lambda Functions',
    href: '/lambda-functions',
  },
  {
    title: 'Reports',
    href: '/reports',
  },
];

export default function Layout() {
  const location = useLocation();

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Full Width Title Bar */}
      <header className="bg-white shadow-sm border-b-4 border-black h-16 flex items-center justify-center px-6 w-full">
        <h1 className="text-2xl font-bold text-gray-900 underline">
          Crypto Forecast Admin
        </h1>
      </header>

      {/* Content Area with Sidebar and Main */}
      <div className="flex flex-1">
        {/* Fixed Sidebar */}
        <div className="bg-white shadow-lg border-r-4 border-gray-200 flex flex-col" style={{ width: '170px' }}>
          {/* Navigation */}
          <nav className="flex-1 pt-0 overflow-y-auto">
            <div className="space-y-1" style={{ paddingLeft: '8%' }}>
              {navigationItems.map((item) => {
                const isActive = location.pathname === item.href;
                const showDivider = item.title === 'Queries History';
                
                return (
                  <div key={item.href}>
                    {showDivider && (
                      <div className="my-3 mx-4">
                        <div className="border-t-4 border-black-300"></div>
                      </div>
                    )}
                    <Link
                      to={item.href}
                      className={`flex items-center py-2 font-normal rounded-lg transition-all duration-200 ${
                        isActive
                          ? 'bg-blue-50 text-blue-700 border-l-6 border-r-4 border-blue-700 underline'
                          : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                      }`}
                      style={{ fontSize: '1.1rem' }}
                    >
                      {item.title}
                    </Link>
                  </div>
                );
              })}
            </div>
          </nav>

          {/* Footer */}
          <div className="p-4 border-t border-gray-200">
            <div className="text-xs text-gray-500 text-center">
              v1.0.0 - Admin Panel
            </div>
          </div>
        </div>

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* Page Content */}
          <main className="flex-1 overflow-auto bg-gray-50">
            <div className="py-6" style={{ paddingLeft: '5%', paddingRight: '10%' }}>
              <Outlet />
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}
