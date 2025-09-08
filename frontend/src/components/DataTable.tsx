import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Input } from '@/components/ui/input';
import type { TableProps, TableColumn } from '@/types';

type SortDirection = 'asc' | 'desc' | null;

interface SortConfig<T> {
  key: keyof T | null;
  direction: SortDirection;
}

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
  const [sortConfig, setSortConfig] = useState<SortConfig<T>>({
    key: null,
    direction: null,
  });

  // Helper function to get searchable text for a record
  const getSearchableText = (record: T) => {
    // Search through all columns instead of filtering by specific titles
    return columns.map(column => {
      if (column.render) {
        // Get the rendered value as a string
        const renderedValue = column.render(record[column.key], record);
        
        // Special handling for Status column which returns JSX with the actual status text
        if (column.title.toLowerCase() === 'status') {
          // For status column, use the raw value instead of rendered JSX
          return String(record[column.key] || '');
        }
        
        // For other columns, convert rendered value to string and remove HTML tags
        return String(renderedValue).replace(/<[^>]*>/g, '');
      } else {
        return String(record[column.key] || '');
      }
    }).join(' ').toLowerCase();
  };

  // Filter data based on search term
  const filteredData = searchable
    ? data.filter((item) => {
        if (!searchTerm.trim()) return true;
        const searchableText = getSearchableText(item);
        return searchableText.includes(searchTerm.toLowerCase());
      })
    : data;

  // Sort data based on sort configuration
  const sortedData = [...filteredData].sort((a, b) => {
    if (!sortConfig.key || !sortConfig.direction) {
      return 0;
    }

    const aValue = a[sortConfig.key];
    const bValue = b[sortConfig.key];

    // Handle null/undefined values
    if (aValue === null || aValue === undefined) {
      return bValue === null || bValue === undefined ? 0 : 1;
    }
    if (bValue === null || bValue === undefined) {
      return -1;
    }

    // Handle different data types
    let comparison = 0;
    
    if (typeof aValue === 'string' && typeof bValue === 'string') {
      // Check if it's a date string
      if (/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/.test(aValue) && /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/.test(bValue)) {
        const dateA = new Date(aValue);
        const dateB = new Date(bValue);
        comparison = dateA.getTime() - dateB.getTime();
      } else {
        comparison = aValue.localeCompare(bValue);
      }
    } else if (typeof aValue === 'number' && typeof bValue === 'number') {
      comparison = aValue - bValue;
    } else {
      // Convert to strings for comparison
      comparison = String(aValue).localeCompare(String(bValue));
    }

    return sortConfig.direction === 'asc' ? comparison : -comparison;
  });

  const handleSort = (key: keyof T) => {
    const column = columns.find(col => col.key === key);
    if (!column?.sortable) return;

    let direction: SortDirection = 'asc';
    
    if (sortConfig.key === key) {
      if (sortConfig.direction === 'asc') {
        direction = 'desc';
      } else if (sortConfig.direction === 'desc') {
        direction = null;
      }
    }

    setSortConfig({ key: direction ? key : null, direction });
  };

  const getSortIcon = (key: keyof T) => {
    const column = columns.find(col => col.key === key);
    if (!column?.sortable) return null;

    const baseClasses = "w-4 h-4 ml-1";
    const svgProps = {
      fill: "none",
      stroke: "currentColor",
      viewBox: "0 0 24 24",
      width: "16",
      height: "16"
    };
    const pathProps = {
      strokeLinecap: "round" as const,
      strokeLinejoin: "round" as const,
      strokeWidth: 2,
      d: "M5 15l7-7 7 7"
    };

    if (sortConfig.key !== key) {
      return (
        <svg className={`${baseClasses} text-gray-400`} {...svgProps}>
          <path {...pathProps} />
        </svg>
      );
    }

    if (sortConfig.direction === 'asc') {
      return (
        <svg className={`${baseClasses} text-blue-600`} {...svgProps}>
          <path {...pathProps} />
        </svg>
      );
    }

    if (sortConfig.direction === 'desc') {
      return (
        <svg className={`${baseClasses} text-blue-600`} {...svgProps} transform="rotate(180)">
          <path {...pathProps} />
        </svg>
      );
    }

    return null;
  };

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
    
    // More precise date detection - check for ISO date format
    if (typeof value === 'string' && /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/.test(value)) {
      try {
        const date = new Date(value);
        if (!isNaN(date.getTime())) {
          return date.toLocaleDateString();
        }
      } catch {
        // Fall through to return as string
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
                    <TableHead 
                      key={String(column.key)}
                      className={column.sortable ? 'cursor-pointer select-none hover:bg-gray-50' : ''}
                      onClick={() => column.sortable && handleSort(column.key)}
                    >
                      <div className="flex items-center">
                        {column.title}
                        {getSortIcon(column.key)}
                      </div>
                    </TableHead>
                  ))}
                  {(onEdit || onDelete || onView) && (
                    <TableHead className="w-32">Actions</TableHead>
                  )}
                </TableRow>
              </TableHeader>
              <TableBody>
                {sortedData.length === 0 ? (
                  <TableRow>
                    <TableCell
                      colSpan={columns.length + (onEdit || onDelete || onView ? 1 : 0)}
                      className="h-24 text-center"
                    >
                      No data available
                    </TableCell>
                  </TableRow>
                ) : (
                  sortedData.map((record, index) => (
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
