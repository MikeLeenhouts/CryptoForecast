import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { eventBridgeRulesApi } from '@/services/api';

interface EventBridgeRule {
  Name: string;
  Arn: string;
  State: string;
  ScheduleExpression: string;
  EventBusName: string;
}

export default function EventBridgeRulesPage() {
  // Fetch EventBridge rules
  const { data: rules = [], isLoading } = useQuery({
    queryKey: ['eventBridgeRules'],
    queryFn: async () => {
      const response = await eventBridgeRulesApi.getAll();
      return response.data;
    },
  });

  const parseScheduleExpression = (expression: string): string => {
    if (!expression) return 'No schedule';
    
    // Handle cron expressions like "cron(0 12 * * ? *)"
    const cronMatch = expression.match(/cron\((.+)\)/);
    if (cronMatch) {
      const cronParts = cronMatch[1].split(' ');
      if (cronParts.length >= 6) {
        const [minute, hour, dayOfMonth, month, dayOfWeek] = cronParts;
        
        // Simple parsing for common patterns
        if (dayOfMonth === '*' && month === '*' && (dayOfWeek === '?' || dayOfWeek === '*')) {
          const hourNum = parseInt(hour);
          const minuteNum = parseInt(minute);
          const timeStr = `${hourNum.toString().padStart(2, '0')}:${minuteNum.toString().padStart(2, '0')}`;
          return `At ${timeStr} UTC every day`;
        }
      }
    }
    
    // Handle rate expressions like "rate(5 minutes)"
    const rateMatch = expression.match(/rate\((\d+)\s+(\w+)\)/);
    if (rateMatch) {
      const [, value, unit] = rateMatch;
      return `Every ${value} ${unit}`;
    }
    
    return expression;
  };

  const getStateColor = (state: string) => {
    switch (state) {
      case 'ENABLED': return 'bg-green-100 text-green-800';
      case 'DISABLED': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold">EventBridge Rules</h2>
      </div>


      {/* Rules Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" style={{ width: '70%' }}>
        {isLoading ? (
          <div className="col-span-full flex items-center justify-center h-32">
            <div className="text-sm text-gray-500">Loading rules...</div>
          </div>
        ) : rules.length === 0 ? (
          <div className="col-span-full flex items-center justify-center h-32">
            <div className="text-sm text-gray-500">No EventBridge rules found</div>
          </div>
        ) : (
          rules.map((rule: EventBridgeRule) => (
            <Card key={rule.Name} className="hover:shadow-md transition-shadow">
              <CardHeader>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-900 leading-tight"><strong>Name":</strong> "{rule.Name}</p>
                <p className="text-sm text-gray-900 break-all leading-tight"><strong>Arn":</strong> "{rule.Arn}</p>
                <p className="text-sm text-gray-900 leading-tight"><strong>State":</strong> "{rule.State}</p>
                <p className="text-sm text-gray-900 leading-tight"><strong>ScheduleExpression":</strong> "{rule.ScheduleExpression}</p>
                <p className="text-sm text-gray-900 leading-tight"><strong>EventBusName":</strong> "{rule.EventBusName}"</p>
                
                <div className="pt-2 border-t border-gray-100">
                  <div className="flex items-center space-x-1">
                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                    <p className="text-sm font-medium text-blue-700">
                      {parseScheduleExpression(rule.ScheduleExpression)}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
