/**
 * Confirm Dialog component.
 * 
 * STUB: Minimal implementation for Phase 1 Batch 2.
 */

interface ConfirmDialogProps {
  title: string
  message: string
  onConfirm: () => void
  onCancel: () => void
  isOpen: boolean
  isLoading?: boolean
  buttonText?: string
  buttonColor?: 'red' | 'blue'
}

export default function ConfirmDialog({
  title,
  message,
  onConfirm,
  onCancel,
  isOpen,
  isLoading = false,
  buttonText = 'Confirm',
  buttonColor = 'red'
}: ConfirmDialogProps) {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-sm mx-4">
        <h2 className="text-xl font-bold mb-4">{title}</h2>
        <p className="text-gray-600 mb-6">{message}</p>
        <div className="flex gap-4 justify-end">
          <button
            onClick={onCancel}
            disabled={isLoading}
            className="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300 disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            disabled={isLoading}
            className={`px-4 py-2 text-white rounded ${
              buttonColor === 'red'
                ? 'bg-red-600 hover:bg-red-700'
                : 'bg-blue-600 hover:bg-blue-700'
            } disabled:opacity-50`}
          >
            {isLoading ? 'Loading...' : buttonText}
          </button>
        </div>
      </div>
    </div>
  )
}
