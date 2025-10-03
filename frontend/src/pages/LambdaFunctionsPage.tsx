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
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
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
              <CardContent>
                <p className="text-sm text-gray-900 leading-tight"><strong>FunctionName:</strong> {func.FunctionName}</p>
                <p className="text-sm text-gray-900 break-all leading-tight"><strong>FunctionArn:</strong> {func.FunctionArn}</p>
                <p className="text-sm text-gray-900 leading-tight"><strong>Runtime:</strong> {func.Runtime}</p>
                <p className="text-sm text-gray-900 break-all leading-tight"><strong>Role:</strong> {func.Role}</p>
                <p className="text-sm text-gray-900 leading-tight"><strong>Handler:</strong> {func.Handler}</p>
                <p className="text-sm text-gray-900 leading-tight"><strong>CodeSize:</strong> {func.CodeSize}</p>
                <p className="text-sm text-gray-900 leading-tight"><strong>Description:</strong> {func.Description || 'No description'}</p>
                <p className="text-sm text-gray-900 leading-tight"><strong>Timeout:</strong> {func.Timeout}</p>
                <p className="text-sm text-gray-900 leading-tight"><strong>MemorySize:</strong> {func.MemorySize}</p>
                <p className="text-sm text-gray-900 leading-tight"><strong>LastModified:</strong> {func.LastModified}</p>
                <p className="text-sm text-gray-900 break-all leading-tight"><strong>CodeSha256:</strong> {func.CodeSha256}</p>
                <p className="text-sm text-gray-900 leading-tight"><strong>Version:</strong> {func.Version}</p>
                <p className="text-sm text-gray-900 leading-tight"><strong>TracingConfig.Mode:</strong> {func.TracingConfig?.Mode}</p>
                <p className="text-sm text-gray-900 break-all leading-tight"><strong>RevisionId:</strong> {func.RevisionId}</p>
                <p className="text-sm text-gray-900 leading-tight"><strong>PackageType:</strong> {func.PackageType}</p>
                <p className="text-sm text-gray-900 leading-tight"><strong>Architectures:</strong> {func.Architectures?.join(', ')}</p>
                <p className="text-sm text-gray-900 leading-tight"><strong>EphemeralStorage.Size:</strong> {func.EphemeralStorage?.Size}</p>
                <p className="text-sm text-gray-900 leading-tight"><strong>SnapStart.ApplyOn:</strong> {func.SnapStart?.ApplyOn}</p>
                <p className="text-sm text-gray-900 leading-tight"><strong>SnapStart.OptimizationStatus:</strong> {func.SnapStart?.OptimizationStatus}</p>
                <p className="text-sm text-gray-900 leading-tight"><strong>LoggingConfig.LogFormat:</strong> {func.LoggingConfig?.LogFormat}</p>
                <p className="text-sm text-gray-900 leading-tight"><strong>LoggingConfig.LogGroup:</strong> {func.LoggingConfig?.LogGroup}</p>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
