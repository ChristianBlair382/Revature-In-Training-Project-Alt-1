import {
  Container,
  Typography,
  Box,
  Snackbar,
  Alert
} from "@mui/material";
import { useState } from "react";
import { AuthProvider, useAuth } from "./context/AuthContext.jsx";
import AppHeader from "./components/layout/AppHeader.jsx";
import LoginForm from "./components/auth/LoginForm.jsx";
import FarmsDataGrid from "./components/farms/FarmsDataGrid.jsx";
import EquipmentsDataGrid from "./components/equipments/EquipmentsDataGrid.jsx";
import FieldJobsDataGrid from "./components/field_jobs/FieldJobsDataGrid.jsx";
import ServiceReportsDataGrid from "./components/service_reports/ServiceReportsDataGrid.jsx";
import HandsDataGrid from "./components/hands/HandsDataGrid.jsx";
import SupervisorsDataGrid from "./components/supervisors/SupervisorsDataGrid.jsx";
import UsersDataGrid from "./components/users/UsersDataGrid.jsx";

function Dashboard() {
  const {user, logout} = useAuth()
  const [notification, setNotification] = useState('')

  const isFOA = user?.role === 'Field_Operations_Admin' || user?.role === 'FOA';

  return (
    <>
      <AppHeader username={user?.sub} role={user?.role} onLogout={logout} />
      <Container>
        <Typography
          sx={{color: "black"}}
          variant="h5"
          component="h2"
          gutterBottom
        >
          Farms
        </Typography>
        <Box sx={{mb: 4}}>
          <FarmsDataGrid onSuccess={setNotification} />
        </Box>
        <Typography
          sx={{color: "black"}}
          variant="h5"
          component="h2"
          gutterBottom
        >
          Equipments
        </Typography>
        <Box sx={{mb: 4}}>
          <EquipmentsDataGrid onSuccess={setNotification} />
        </Box>
        <Typography
          sx={{color: "black"}}
          variant="h5"
          component="h2"
          gutterBottom
        >
          Field Jobs
        </Typography>
        <Box sx={{mb: 4}}>
          <FieldJobsDataGrid onSuccess={setNotification} />
        </Box>
        <Typography
          sx={{color: "black"}}
          variant="h5"
          component="h2"
          gutterBottom
        >
          Service Reports
        </Typography>
        <Box sx={{mb: 4}}>
          <ServiceReportsDataGrid onSuccess={setNotification} />
        </Box>
        <Typography
          sx={{color: "black"}}
          variant="h5"
          component="h2"
          gutterBottom
        >
          Hands
        </Typography>
        <Box sx={{mb: 4}}>
          <HandsDataGrid onSuccess={setNotification} />
        </Box>
        <Typography
          sx={{color: "black"}}
          variant="h5"
          component="h2"
          gutterBottom
        >
          Supervisors
        </Typography>
        <Box sx={{mb: 4}}>
          <SupervisorsDataGrid onSuccess={setNotification} />
        </Box>
        { isFOA &&
          <>
            <Typography
            sx={{color: "black"}}
            variant="h5"
            component="h2"
            gutterBottom
            >
              Users
            </Typography>
            <Box sx={{mb: 4}}>
              <UsersDataGrid onSuccess={setNotification}/>
            </Box>
          </>
        }
      </Container>

      <Snackbar 
        open={Boolean(notification)}
        autoHideDuration={4000}
        onClose={() => setNotification(null)}
      >
        <Alert severity="success" onClose={() => setNotification(null)}>{notification}</Alert>
      </Snackbar>
    </>
  );
}

function AppContent() {
  const {isAuthenticated} = useAuth();
  return isAuthenticated ? <Dashboard /> : <LoginForm />;
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}

export default App