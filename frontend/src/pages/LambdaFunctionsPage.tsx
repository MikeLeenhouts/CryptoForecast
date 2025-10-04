import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { lambdaFunctionsApi } from '@/services/api';

interface LambdaFunction {
  FunctionName: string;
  FunctionArn: string;
  Runtime: string;
  Role: string;
  Handler: string;
  CodeSize: number;
  Description: string;
  Timeout: number;
  MemorySize: number;
  LastModified: string;
  CodeSha256: string;
  Version: string;
  TracingConfig: {
    Mode: string;
  };
  RevisionId: string;
  PackageType: string;
  Architectures: string[];
  EphemeralStorage: {
    Size: number;
  };
  SnapStart: {
    ApplyOn: string;
    OptimizationStatus: string;
  };
  LoggingConfig: {
    LogFormat: string;
    LogGroup: string;
  };
}

export default function LambdaFunctionsPage() {
  // Fetch Lambda functions
  const { data: functions = [], isLoading } = useQuery({
    queryKey: ['lambdaFunctions'],
    queryFn: async () => {
      const response = await lambdaFunctionsApi.getAll();
      return response.data;
    },
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold">Lambda Functions</h2>
      </div>

      {/* Functions Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" style={{ width: '70%' }}>
        {isLoading ? (
          <div className="col-span-full flex items-center justify-center h-32">
            <div className="text-sm text-gray-500">Loading functions...</div>
          </div>
        ) : functions.length === 0 ? (
          <div className="col-span-full flex items-center justify-center h-32">
            <div className="text-sm text-gray-500">No Lambda functions found</div>
          </div>
        ) : (
          functions.map((func: LambdaFunction) => (
            <Card key={func.FunctionName} className="hover:shadow-md transition-shadow">
              <CardHeader>
              </CardHeader>
              <CardContent className="p-4">
                <pre className="text-xs text-gray-900 whitespace-pre-wrap break-words font-mono">
                  {JSON.stringify(func, null, 2)}
                </pre>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
