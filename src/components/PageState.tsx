import React from 'react';
import { Loader, Notification } from '@kiki/ui';

interface PageStateProps {
  isLoading?: boolean;
  isError?: boolean;
  errorMessage?: string;
  isEmpty?: boolean;
  emptyMessage?: string;
  children: React.ReactNode;
}

const PageState: React.FC<PageStateProps> = ({
  isLoading = false,
  isError = false,
  errorMessage = 'An error occurred.',
  isEmpty = false,
  emptyMessage = 'No data to display.',
  children,
}) => {
  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[40vh]">
        <Loader size="lg" />
        <span className="mt-4 text-gray-400">Loading...</span>
      </div>
    );
  }
  if (isError) {
    return (
      <Notification type="error" message={errorMessage} />
    );
  }
  if (isEmpty) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[40vh]">
        <span className="text-gray-400">{emptyMessage}</span>
      </div>
    );
  }
  return <>{children}</>;
};

export default PageState;
