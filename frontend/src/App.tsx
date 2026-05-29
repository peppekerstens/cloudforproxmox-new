import { useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './stores/authStore'
import { useConfigStore } from './stores/configStore'
import Layout from './components/Layout'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import VMsPage from './pages/VMsPage'
import CreateVMPage from './pages/CreateVMPage'
import VMDetailPage from './pages/VMDetailPage'
import ClustersPage from './pages/ClustersPage'
import ClusterDetailPage from './pages/ClusterDetailPage'
import CreateClusterPage from './pages/CreateClusterPage'
import OrganizationSettingsPage from './pages/OrganizationSettingsPage'
import QuotaPage from './pages/QuotaPage'
import ISOUploadPage from './pages/ISOUploadPage'
import NetworksPage from './pages/NetworksPage'
import ContainersPage from './pages/ContainersPage'
import CreateContainerPage from './pages/CreateContainerPage'
import AdminUsersPage from './pages/AdminUsersPage'
import AdminOrganizationsPage from './pages/AdminOrganizationsPage'
import AdminQuotasPage from './pages/AdminQuotasPage'
import DNSAdminPage from './pages/DNSAdminPage'
import AdminNetworkingPage from './pages/AdminNetworkingPage'
import AdminBrandingPage from './pages/AdminBrandingPage'
import TemplatesPage from './pages/TemplatesPage'
import RolesManagementPage from './pages/RolesManagementPage'
import BillingPage from './pages/BillingPage'
import AdminBillingPage from './pages/AdminBillingPage'
import PaymentSuccessPage from './pages/PaymentSuccessPage'
import PaymentCancelPage from './pages/PaymentCancelPage'
import AuditLogsPage from './pages/AuditLogsPage'
import AdminAuditLogsPage from './pages/AdminAuditLogsPage'
import AdminCertificatePage from './pages/AdminCertificatePage'

function App() {
  const { isAuthenticated } = useAuthStore()
  const applyBranding = useConfigStore((state) => state.applyBranding)
  const branding = useConfigStore((state) => state.branding)

  useEffect(() => {
    applyBranding()
  }, [branding, applyBranding])

  return (
    <Routes>
      <Route
        path="/login"
        element={isAuthenticated ? <Navigate to="/dashboard" /> : <LoginPage />}
      />
      <Route
        path="/register"
        element={isAuthenticated ? <Navigate to="/dashboard" /> : <RegisterPage />}
      />
      <Route
        path="/dashboard"
        element={
          isAuthenticated ? (
            <Layout>
              <DashboardPage />
            </Layout>
          ) : (
            <Navigate to="/login" />
          )
        }
      />
      <Route
        path="/vms"
        element={
          isAuthenticated ? (
            <Layout>
              <VMsPage />
            </Layout>
          ) : (
            <Navigate to="/login" />
          )
        }
      />
      <Route
        path="/vms/create"
        element={
          isAuthenticated ? (
            <Layout>
              <CreateVMPage />
            </Layout>
          ) : (
            <Navigate to="/login" />
          )
        }
      />
      <Route
        path="/vms/:vmId"
        element={
          isAuthenticated ? (
            <Layout>
              <VMDetailPage />
            </Layout>
          ) : (
            <Navigate to="/login" />
          )
        }
      />
      <Route
        path="/templates"
        element={<Navigate to="/vm-templates/templates" replace />}
      />
      <Route
        path="/vm-templates"
        element={<Navigate to="/vm-templates/templates" replace />}
      />
      <Route
        path="/vm-templates/templates"
        element={
          isAuthenticated ? (
            <Layout>
              <TemplatesPage />
            </Layout>
          ) : (
            <Navigate to="/login" />
          )
        }
      />
      <Route
        path="/vm-templates/isos"
        element={
          isAuthenticated ? (
            <Layout>
              <ISOUploadPage />
            </Layout>
          ) : (
            <Navigate to="/login" />
          )
        }
      />
      <Route
        path="/clusters"
        element={
          isAuthenticated ? (
            <Layout>
              <ClustersPage />
            </Layout>
          ) : (
            <Navigate to="/login" />
          )
        }
      />
      <Route
        path="/clusters/create"
        element={
          isAuthenticated ? (
            <Layout>
              <CreateClusterPage />
            </Layout>
          ) : (
            <Navigate to="/login" />
          )
        }
      />
      <Route
        path="/clusters/:id"
        element={
          isAuthenticated ? (
            <Layout>
              <ClusterDetailPage />
            </Layout>
          ) : (
            <Navigate to="/login" />
          )
        }
      />
      <Route
        path="/quotas"
        element={
          isAuthenticated ? (
            <Layout>
              <QuotaPage />
            </Layout>
          ) : (
            <Navigate to="/login" />
          )
        }
      />
      <Route
        path="/containers"
        element={
          isAuthenticated ? (
            <Layout>
              <ContainersPage />
            </Layout>
          ) : (
            <Navigate to="/login" />
          )
        }
      />
      <Route
        path="/containers/create"
        element={
          isAuthenticated ? (
            <Layout>
              <CreateContainerPage />
            </Layout>
          ) : (
            <Navigate to="/login" />
          )
        }
      />
      <Route
        path="/networking"
        element={
          isAuthenticated ? (
            <Layout>
              <NetworksPage />
            </Layout>
          ) : (
            <Navigate to="/login" />
          )
        }
      />
      <Route
        path="/settings"
        element={<Navigate to="/organization/settings" replace />}
      />
      <Route
        path="/organization/settings"
        element={
          isAuthenticated ? (
            <Layout>
              <OrganizationSettingsPage />
            </Layout>
          ) : (
            <Navigate to="/login" />
          )
        }
      />
       <Route
         path="/organization/roles"
         element={
           isAuthenticated ? (
             <Layout>
               <RolesManagementPage />
             </Layout>
           ) : (
             <Navigate to="/login" />
           )
         }
       />
       <Route
         path="/organization/audit-logs"
         element={
           isAuthenticated ? (
             <Layout>
               <AuditLogsPage />
             </Layout>
           ) : (
             <Navigate to="/login" />
           )
         }
       />
      <Route
        path="/admin/users"
        element={
          isAuthenticated ? (
            <Layout>
              <AdminUsersPage />
            </Layout>
          ) : (
            <Navigate to="/login" />
          )
        }
      />
      <Route
        path="/admin/organizations"
        element={
          isAuthenticated ? (
            <Layout>
              <AdminOrganizationsPage />
            </Layout>
          ) : (
            <Navigate to="/login" />
          )
        }
      />
      <Route
        path="/admin/quotas"
        element={
          isAuthenticated ? (
            <Layout>
              <AdminQuotasPage />
            </Layout>
          ) : (
            <Navigate to="/login" />
          )
        }
      />
      <Route
        path="/admin/dns"
        element={
          isAuthenticated ? (
            <Layout>
              <DNSAdminPage />
            </Layout>
          ) : (
            <Navigate to="/login" />
          )
        }
      />
      <Route
        path="/admin/networking"
        element={
          isAuthenticated ? (
            <Layout>
              <AdminNetworkingPage />
            </Layout>
          ) : (
            <Navigate to="/login" />
          )
        }
      />
      <Route
        path="/admin/branding"
        element={
          isAuthenticated ? (
            <Layout>
              <AdminBrandingPage />
            </Layout>
          ) : (
            <Navigate to="/login" />
          )
        }
      />
      <Route
        path="/billing"
        element={
          isAuthenticated ? (
            <Layout>
              <BillingPage />
            </Layout>
          ) : (
            <Navigate to="/login" />
          )
        }
      />
      <Route
        path="/admin/billing"
        element={
          isAuthenticated ? (
            <Layout>
              <AdminBillingPage />
            </Layout>
          ) : (
            <Navigate to="/login" />
          )
        }
      />
       <Route
          path="/admin/audit-logs"
          element={
            isAuthenticated ? (
              <Layout>
                <AdminAuditLogsPage />
              </Layout>
            ) : (
              <Navigate to="/login" />
            )
          }
        />
        <Route
          path="/admin/certificates"
          element={
            isAuthenticated ? (
              <Layout>
                <AdminCertificatePage />
              </Layout>
            ) : (
              <Navigate to="/login" />
            )
          }
        />
       <Route path="/payment/success" element={<PaymentSuccessPage />} />
      <Route path="/payment/cancel" element={<PaymentCancelPage />} />
      <Route
        path="/"
        element={<Navigate to={isAuthenticated ? "/dashboard" : "/login"} />}
      />
    </Routes>
  )
}

export default App
