import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
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
    
    // Handle cron expressions like "cron(29 13 ? * MON-FRI *)"
    const cronMatch = expression.match(/cron\((.+)\)/);
    if (cronMatch) {
      const cronParts = cronMatch[1].split(' ');
      if (cronParts.length >= 6) {
        const [minute, hour, dayOfMonth, month, dayOfWeek] = cronParts;
        
        // Parse time
        const hourNum = parseInt(hour);
        const minuteNum = parseInt(minute);
        let timeStr = '';
        
        if (hourNum === 0 && minuteNum === 0) {
          timeStr = '12:00AM';
        } else if (hourNum === 12) {
          timeStr = `12:${minuteNum.toString().padStart(2, '0')}PM`;
        } else if (hourNum > 12) {
          timeStr = `${(hourNum - 12).toString()}:${minuteNum.toString().padStart(2, '0')}PM`;
        } else {
          timeStr = `${hourNum.toString()}:${minuteNum.toString().padStart(2, '0')}AM`;
        }
        
        // Parse day of week
        let dayStr = '';
        if (dayOfWeek === '?' || dayOfWeek === '*') {
          dayStr = 'every day';
        } else if (dayOfWeek === 'MON-FRI') {
          dayStr = 'Monday-Friday';
        } else if (dayOfWeek === 'SAT,SUN') {
          dayStr = 'Saturday-Sunday';
        } else if (dayOfWeek.includes('-')) {
          // Handle ranges like MON-FRI
          const dayMap: { [key: string]: string } = {
            'SUN': 'Sunday', 'MON': 'Monday', 'TUE': 'Tuesday', 'WED': 'Wednesday',
            'THU': 'Thursday', 'FRI': 'Friday', 'SAT': 'Saturday'
          };
          const [start, end] = dayOfWeek.split('-');
          dayStr = `${dayMap[start]}-${dayMap[end]}`;
        } else if (dayOfWeek.includes(',')) {
          // Handle comma-separated days
          const dayMap: { [key: string]: string } = {
            'SUN': 'Sunday', 'MON': 'Monday', 'TUE': 'Tuesday', 'WED': 'Wednesday',
            'THU': 'Thursday', 'FRI': 'Friday', 'SAT': 'Saturday'
          };
          const days = dayOfWeek.split(',').map(d => dayMap[d.trim()]).join(', ');
          dayStr = days;
        } else {
          // Single day
          const dayMap: { [key: string]: string } = {
            'SUN': 'Sunday', 'MON': 'Monday', 'TUE': 'Tuesday', 'WED': 'Wednesday',
            'THU': 'Thursday', 'FRI': 'Friday', 'SAT': 'Saturday'
          };
          dayStr = dayMap[dayOfWeek] || dayOfWeek;
        }
        
        // Handle day of month
        if (dayOfMonth !== '*' && dayOfMonth !== '?') {
          if (dayOfMonth.includes('/')) {
            // Handle intervals like */5 (every 5 days)
            const [, interval] = dayOfMonth.split('/');
            dayStr = `every ${interval} days`;
          } else {
            dayStr = `on the ${dayOfMonth}${getOrdinalSuffix(parseInt(dayOfMonth))} of the month`;
          }
        }
        
        // Handle month
        let monthStr = '';
        if (month !== '*') {
          const monthMap: { [key: string]: string } = {
            '1': 'January', '2': 'February', '3': 'March', '4': 'April',
            '5': 'May', '6': 'June', '7': 'July', '8': 'August',
            '9': 'September', '10': 'October', '11': 'November', '12': 'December'
          };
          monthStr = ` in ${monthMap[month]}`;
        }
        
        return `${timeStr} UTC ${dayStr}${monthStr}`;
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

  const getOrdinalSuffix = (num: number): string => {
    const j = num % 10;
    const k = num % 100;
    if (j === 1 && k !== 11) return 'st';
    if (j === 2 && k !== 12) return 'nd';
    if (j === 3 && k !== 13) return 'rd';
    return 'th';
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
