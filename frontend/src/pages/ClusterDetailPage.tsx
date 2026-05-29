import { useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ArrowLeft, Server, CheckCircle, XCircle, RefreshCw, Trash2, Cpu, HardDrive, MemoryStick } from 'lucide-react'
import { clustersApi } from '../services/api'
import { toast } from '../lib/toast'
import ConfirmDialog from '../components/ui/ConfirmDialog'

export default function ClusterDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)

  const { data: cluster, isLoading, error } = useQuery({
    queryKey: ['cluster', id],
    queryFn: () => clustersApi.get(id!),
    enabled: !!id,
  })

  const syncMutation = useMutation({
    mutationFn: () => clustersApi.sync(id!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cluster', id] })
      toast.success('Cluster synced')
    },
    onError: () => {
      toast.error('Failed to sync cluster')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: () => clustersApi.delete(id!),
    onSuccess: () => {
      navigate('/clusters')
      toast.success('Cluster deleted')
    },
    onError: () => {
      toast.error('Failed to delete cluster')
    },
  })

  const handleDelete = () => {
    setShowDeleteConfirm(true)
  }

  const confirmDelete = () => {
    setShowDeleteConfirm(false)
    deleteMutation.mutate()
  }

  const handleSync = () => {
    syncMutation.mutate()
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-gray-600">Loading cluster...</div>
      </div>
    )
  }

  if (error || !cluster) {
    return (
      <div className="p-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <p className="text-red-600">Cluster not found or failed to load.</p>
          <Link to="/clusters" className="text-indigo-600 hover:text-indigo-900 mt-2 inline-block">
            Back to Clusters
          </Link>
        </div>
      </div>
    )
  }

  const formatBytes = (mb: number) => {
    if (!mb) return '0 GB'
    if (mb >= 1024) return `${(mb / 1024).toFixed(1)} GB`
    return `${mb} MB`
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <Link
          to="/clusters"
          className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft className="w-4 h-4 mr-1" />
          Back to Clusters
        </Link>
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center">
              <Server className="w-8 h-8 mr-3 text-gray-400" />
              {cluster.name}
            </h1>
            <p className="text-gray-600 mt-1">{cluster.api_url}</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleSync}
              disabled={syncMutation.isPending}
              className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
            >
              <RefreshCw className={`w-5 h-5 mr-2 ${syncMutation.isPending ? 'animate-spin' : ''}`} />
              Sync
            </button>
            <button
              onClick={handleDelete}
              disabled={deleteMutation.isPending}
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700 disabled:opacity-50"
            >
              <Trash2 className="w-5 h-5 mr-2" />
              Delete
            </button>
          </div>
        </div>
      </div>

      {/* Status */}
      <div className="mb-6">
        {cluster.is_active ? (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
            <CheckCircle className="w-4 h-4 mr-1" />
            Active
          </span>
        ) : (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800">
            <XCircle className="w-4 h-4 mr-1" />
            Inactive
          </span>
        )}
      </div>

      {/* Details Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {/* Connection */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Connection</h2>
          <dl className="space-y-3">
            <div>
              <dt className="text-sm font-medium text-gray-500">API URL</dt>
              <dd className="text-sm text-gray-900 break-all">{cluster.api_url}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Username</dt>
              <dd className="text-sm text-gray-900">{cluster.api_username}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">SSL Verification</dt>
              <dd className="text-sm text-gray-900">{cluster.verify_ssl ? 'Enabled' : 'Disabled'}</dd>
            </div>
          </dl>
        </div>

        {/* Location */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Location</h2>
          <dl className="space-y-3">
            <div>
              <dt className="text-sm font-medium text-gray-500">Datacenter</dt>
              <dd className="text-sm text-gray-900">{cluster.datacenter || '-'}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Region</dt>
              <dd className="text-sm text-gray-900">{cluster.region || '-'}</dd>
            </div>
          </dl>
        </div>

        {/* Resources */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Resources</h2>
          <dl className="space-y-3">
            <div className="flex items-center">
              <Cpu className="w-5 h-5 text-gray-400 mr-2" />
              <dt className="text-sm font-medium text-gray-500">CPU Cores</dt>
            </div>
            <dd className="text-sm text-gray-900 ml-7">{cluster.total_cpu_cores || 0}</dd>
            <div className="flex items-center">
              <MemoryStick className="w-5 h-5 text-gray-400 mr-2" />
              <dt className="text-sm font-medium text-gray-500">Memory</dt>
            </div>
            <dd className="text-sm text-gray-900 ml-7">{formatBytes(cluster.total_memory_mb || 0)}</dd>
            <div className="flex items-center">
              <HardDrive className="w-5 h-5 text-gray-400 mr-2" />
              <dt className="text-sm font-medium text-gray-500">Storage</dt>
            </div>
            <dd className="text-sm text-gray-900 ml-7">{cluster.total_storage_gb ? `${cluster.total_storage_gb} GB` : '-'}</dd>
          </dl>
        </div>
      </div>

      {/* Metadata */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Metadata</h2>
        <dl className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <dt className="text-sm font-medium text-gray-500">Created</dt>
            <dd className="text-sm text-gray-900">{new Date(cluster.created_at).toLocaleString()}</dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500">Last Updated</dt>
            <dd className="text-sm text-gray-900">{new Date(cluster.updated_at).toLocaleString()}</dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500">Last Sync</dt>
            <dd className="text-sm text-gray-900">{cluster.last_sync ? new Date(cluster.last_sync).toLocaleString() : 'Never'}</dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500">Cluster ID</dt>
            <dd className="text-sm text-gray-900 font-mono">{cluster.id}</dd>
          </div>
        </dl>
      </div>

      <ConfirmDialog
        isOpen={showDeleteConfirm}
        title="Delete Cluster"
        message={`Delete cluster "${cluster?.name}"? This action cannot be undone.`}
        onConfirm={confirmDelete}
        onCancel={() => setShowDeleteConfirm(false)}
        loading={deleteMutation.isPending}
      />
    </div>
  )
}
