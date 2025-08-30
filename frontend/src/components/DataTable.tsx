import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Input } from '@/components/ui/input';
import type { TableProps, TableColumn } from '@/types';

interface DataTableProps<T> extends TableProps<T> {
  title: string;
  onAdd?: () => void;
  searchable?: boolean;
  searchPlaceholder?: string;
}

export default function DataTable<T extends Record<string, any>>({
  title,
  data,
  columns,
  loading = false,
  onAdd,
  onEdit,
  onDelete,
  onView,
  searchable = true,
  searchPlaceholder = 'Search...',
}: DataTableProps<T>) {
  const [searchTerm, setSearchTerm] = useState('');

  // Filter data based on search term
  const filteredData = searchable
    ? data.filter((item) =>
        Object.values(item).some((value) =>
          String(value).toLowerCase().includes(searchTerm.toLowerCase())
        )
      )
    : data;

  const renderCellValue = (column: TableColumn<T>, record: T) => {
    const value = record[column.key];
    
    if (column.render) {
      return column.render(value, record);
    }
    
    // Handle different data types
    if (value === null || value === undefined) {
      return '-';
    }
    
    if (typeof value === 'boolean') {
      return value ? 'Yes' : 'No';
    }
    
    if (typeof value === 'string' && value.includes('T')) {
      // Likely a date string
      try {
        return new Date(value).toLocaleDateString();
      } catch {
        return String(value);
      }
    }
    
    return String(value);
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>{title}</CardTitle>
          {onAdd && (
            <Button onClick={onAdd}>
              Add New
            </Button>
          )}
        </div>
        {searchable && (
          <div className="w-full max-w-sm">
            <Input
              placeholder={searchPlaceholder}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full"
            />
          </div>
        )}
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="flex items-center justify-center h-32">
            <div className="text-sm text-gray-500">Loading...</div>
          </div>
        ) : (
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  {columns.map((column) => (
                    <TableHead key={String(column.key)}>
                      {column.title}
                    </TableHead>
                  ))}
                  {(onEdit || onDelete || onView) && (
                    <TableHead className="w-32">Actions</TableHead>
                  )}
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredData.length === 0 ? (
                  <TableRow>
                    <TableCell
                      colSpan={columns.length + (onEdit || onDelete || onView ? 1 : 0)}
                      className="h-24 text-center"
                    >
                      No data available
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredData.map((record, index) => (
                    <TableRow key={index}>
                      {columns.map((column) => (
                        <TableCell key={String(column.key)}>
                          {renderCellValue(column, record)}
                        </TableCell>
                      ))}
                      {(onEdit || onDelete || onView) && (
                        <TableCell>
                          <div className="flex items-center gap-2">
                            {onView && (
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => onView(record)}
                              >
                                View
                              </Button>
                            )}
                            {onEdit && (
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => onEdit(record)}
                              >
                                Edit
                              </Button>
                            )}
                            {onDelete && (
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => onDelete(record)}
                                className="text-red-600 hover:text-red-700"
                              >
                                Delete
                              </Button>
                            )}
                          </div>
                        </TableCell>
                      )}
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
