import { 
  CheckCircle2, 
  XCircle, 
  AlertCircle, 
  Info,
  Loader2 
} from 'lucide-react';

export function EmptyState({ icon: Icon, title, description, action }) {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center bg-white rounded-lg border border-gray-200 border-dashed">
      <div className="w-12 h-12 bg-gray-50 rounded-full flex items-center justify-center mb-4">
        {Icon ? <Icon className="text-gray-400" size={24} /> : <Info className="text-gray-400" size={24} />}
      </div>
      <h3 className="text-lg font-medium text-gray-900 mb-1">{title}</h3>
      {description && <p className="text-sm text-gray-500 mb-6 max-w-sm">{description}</p>}
      {action && <div>{action}</div>}
    </div>
  );
}

export function LoadingState({ message = "Loading..." }) {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center h-64">
      <Loader2 className="h-8 w-8 text-blue-600 animate-spin mb-4" />
      <p className="text-sm text-gray-500">{message}</p>
    </div>
  );
}

export function ErrorState({ title = "Something went wrong", description, onRetry }) {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center bg-red-50 rounded-lg border border-red-100">
      <AlertCircle className="h-10 w-10 text-red-500 mb-4" />
      <h3 className="text-lg font-medium text-red-900 mb-1">{title}</h3>
      {description && <p className="text-sm text-red-700 mb-6 max-w-md">{description}</p>}
      {onRetry && (
        <button 
          onClick={onRetry}
          className="px-4 py-2 bg-red-600 text-white rounded-md text-sm font-medium hover:bg-red-700 transition-colors"
        >
          Try Again
        </button>
      )}
    </div>
  );
}

export function ConfirmationDialog({ isOpen, title, description, confirmText = "Confirm", cancelText = "Cancel", onConfirm, onCancel, type = "danger" }) {
  if (!isOpen) return null;

  const btnClass = type === 'danger' 
    ? 'bg-red-600 hover:bg-red-700 focus:ring-red-500'
    : 'bg-blue-600 hover:bg-blue-700 focus:ring-blue-500';

  const Icon = type === 'danger' ? AlertCircle : Info;
  const iconColor = type === 'danger' ? 'text-red-600 bg-red-100' : 'text-blue-600 bg-blue-100';

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" onClick={onCancel}></div>
        <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div className="sm:flex sm:items-start">
              <div className={`mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full sm:mx-0 sm:h-10 sm:w-10 ${iconColor}`}>
                <Icon className="h-6 w-6" aria-hidden="true" />
              </div>
              <div className="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
                <h3 className="text-lg leading-6 font-medium text-gray-900" id="modal-title">{title}</h3>
                <div className="mt-2">
                  <p className="text-sm text-gray-500">{description}</p>
                </div>
              </div>
            </div>
          </div>
          <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button 
              type="button" 
              className={`w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 text-base font-medium text-white focus:outline-none focus:ring-2 focus:ring-offset-2 sm:ml-3 sm:w-auto sm:text-sm ${btnClass}`}
              onClick={onConfirm}
            >
              {confirmText}
            </button>
            <button 
              type="button" 
              className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
              onClick={onCancel}
            >
              {cancelText}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
