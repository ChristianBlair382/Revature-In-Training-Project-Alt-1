import {
  Container,
  Typography,
  Box,
  Snackbar,
  Alert,
  Card,
  CardContent,
  CircularProgress,
  List,
  ListItem
} from "@mui/material";
import { useEffect, useState } from "react";
import { AuthProvider, useAuth } from "./context/AuthContext.jsx";
import apiClient from "./api/client.js";
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
  const [completionSummary, setCompletionSummary] = useState([])
  const [completionSummaryLoading, setCompletionSummaryLoading] = useState(true)
  const [completionSummaryError, setCompletionSummaryError] = useState(false)
  const [maintenanceFarmSummary, setMaintenanceFarmSummary] = useState([])
  const [maintenanceFarmSummaryLoading, setMaintenanceFarmSummaryLoading] = useState(true)
  const [maintenanceFarmSummaryError, setMaintenanceFarmSummaryError] = useState(false)
  const [supervisorHandSummary, setSupervisorHandSummary] = useState([])
  const [supervisorHandSummaryLoading, setSupervisorHandSummaryLoading] = useState(true)
  const [supervisorHandSummaryError, setSupervisorHandSummaryError] = useState(false)
  const [completionRefreshKey, setCompletionRefreshKey] = useState(0)

  const isFOA = user?.role === 'Field_Operations_Admin' || user?.role === 'FOA';

  useEffect(() => {
    let cancelled = false;

    async function fetchCompletionSummary() {
      setCompletionSummaryLoading(true);
      setCompletionSummaryError(false);
      setMaintenanceFarmSummaryLoading(true);
      setMaintenanceFarmSummaryError(false);
      setSupervisorHandSummaryLoading(true);
      setSupervisorHandSummaryError(false);

      const [equipmentResult, fieldJobsResult, farmsResult, handsResult, supervisorsResult] = await Promise.allSettled([
        apiClient.get('/equipments'),
        apiClient.get('/field_jobs'),
        apiClient.get('/farms'),
        apiClient.get('/hands'),
        apiClient.get('/supervisors'),
      ]);

      if (!cancelled) {
        if (equipmentResult.status === 'fulfilled' && fieldJobsResult.status === 'fulfilled') {
          const equipments = equipmentResult.value.data;
          const completedEquipmentIds = new Set(
            fieldJobsResult.value.data
              .filter((fieldJob) => fieldJob.status === 'Completed')
              .map((fieldJob) => fieldJob.equipment_id)
          );
          const models = new Map();

          equipments.forEach((equipment) => {
            if (!models.has(equipment.model)) {
              models.set(equipment.model, {model: equipment.model, total: 0, completedIds: new Set()});
            }

            const modelSummary = models.get(equipment.model);
            modelSummary.total += 1;
            if (completedEquipmentIds.has(equipment.id)) {
              modelSummary.completedIds.add(equipment.id);
            }
          });

          setCompletionSummary(Array.from(models.values()).map(({model, total, completedIds}) => ({
            model,
            total,
            completed: completedIds.size,
            percentage: Math.round((completedIds.size / total) * 100),
          })));
        } else {
          setCompletionSummaryError(true);
        }

        if (equipmentResult.status === 'fulfilled' && farmsResult.status === 'fulfilled') {
          const farmsById = new Map(
            farmsResult.value.data.map((farm) => [farm.id, {name: farm.name, total: 0, maintenance: 0}])
          );

          equipmentResult.value.data.forEach((equipment) => {
            const farmSummary = farmsById.get(equipment.farm_id);
            if (!farmSummary) return;

            farmSummary.total += 1;
            if (equipment.status === 'Maintenance') farmSummary.maintenance += 1;
          });

          setMaintenanceFarmSummary(Array.from(farmsById.values())
            .filter(({total, maintenance}) => total > 0 && maintenance / total >= 0.3)
            .map(({name, total, maintenance}) => ({
              name,
              total,
              maintenance,
              percentage: Math.round((maintenance / total) * 100),
            })));
        } else {
          setMaintenanceFarmSummaryError(true);
        }

        if (
          fieldJobsResult.status === 'fulfilled' &&
          farmsResult.status === 'fulfilled' &&
          handsResult.status === 'fulfilled' &&
          supervisorsResult.status === 'fulfilled'
        ) {
          const farmsById = new Map(farmsResult.value.data.map((farm) => [farm.id, farm]));
          const supervisorsById = new Map(
            supervisorsResult.value.data.map((supervisor) => [supervisor.id, {id: supervisor.id, name: supervisor.name, handCount: 0}])
          );
          const inProgressHandIds = new Set(
            fieldJobsResult.value.data
              .filter((fieldJob) => fieldJob.status === 'In-Progress')
              .map((fieldJob) => fieldJob.hand_id)
          );

          handsResult.value.data.forEach((hand) => {
            if (!inProgressHandIds.has(hand.id)) return;

            const farm = farmsById.get(hand.farm_id);
            const supervisorSummary = farm && supervisorsById.get(farm.supervisor_id);
            if (supervisorSummary) supervisorSummary.handCount += 1;
          });

          const farmSupervisorIds = new Set(
            farmsResult.value.data.map((farm) => farm.supervisor_id)
          );
          setSupervisorHandSummary(Array.from(supervisorsById.values())
            .filter((supervisor) => farmSupervisorIds.has(supervisor.id)));
        } else {
          setSupervisorHandSummaryError(true);
        }

        setCompletionSummaryLoading(false);
        setMaintenanceFarmSummaryLoading(false);
        setSupervisorHandSummaryLoading(false);
      }
    }

    fetchCompletionSummary();
    return () => {
      cancelled = true;
    };
  }, [completionRefreshKey]);

  const handleGridSuccess = (message) => {
    setNotification(message);
    setCompletionRefreshKey((currentKey) => currentKey + 1);
  };

  return (
    <>
      <AppHeader username={user?.sub} role={user?.role} onLogout={logout} />
      <Box sx={{display: 'grid', gridTemplateColumns: {xs: '1fr', md: 'repeat(3, minmax(0, 1fr))'}, gap: 2, px: 3, py: 2}}>
        <Card variant="outlined">
          <CardContent>
            <Typography variant="h6" component="h2" sx={{color: 'black'}}>
              Completed Field Jobs by Equipment Model
            </Typography>
            {completionSummaryLoading ? (
              <CircularProgress size={24} sx={{mt: 2}} />
            ) : completionSummaryError ? (
              <Alert severity="error" sx={{mt: 2}}>Could not load equipment completion data.</Alert>
            ) : completionSummary.length === 0 ? (
              <Typography sx={{mt: 2}}>No equipment found.</Typography>
            ) : (
              <List disablePadding sx={{mt: 1}}>
                {completionSummary.map(({model, completed, total, percentage}) => (
                  <ListItem key={model} divider disableGutters sx={{gap: 2}}>
                    <Typography sx={{flex: 1}}>{model}</Typography>
                    <Typography aria-label={`${completed} of ${total} equipment have completed field jobs`}>
                      {percentage}%
                    </Typography>
                  </ListItem>
                ))}
              </List>
            )}
          </CardContent>
        </Card>
        <Card variant="outlined">
          <CardContent>
            <Typography variant="h6" component="h2" sx={{color: 'black'}}>
              Farms with 30%+ Equipment in Maintenance
            </Typography>
            {maintenanceFarmSummaryLoading ? (
              <CircularProgress size={24} sx={{mt: 2}} />
            ) : maintenanceFarmSummaryError ? (
              <Alert severity="error" sx={{mt: 2}}>Could not load farm maintenance data.</Alert>
            ) : maintenanceFarmSummary.length === 0 ? (
              <Typography sx={{mt: 2}}>No farms meet the maintenance threshold.</Typography>
            ) : (
              <List disablePadding sx={{mt: 1}}>
                {maintenanceFarmSummary.map(({name, maintenance, total, percentage}) => (
                  <ListItem key={name} divider disableGutters sx={{gap: 2}}>
                    <Typography sx={{flex: 1}}>{name}</Typography>
                    <Typography aria-label={`${maintenance} of ${total} equipment are in maintenance`}>
                      {percentage}%
                    </Typography>
                  </ListItem>
                ))}
              </List>
            )}
          </CardContent>
        </Card>
        <Card variant="outlined">
          <CardContent>
            <Typography variant="h6" component="h2" sx={{color: 'black'}}>
              Hands with In-Progress Field Jobs by Supervisor
            </Typography>
            {supervisorHandSummaryLoading ? (
              <CircularProgress size={24} sx={{mt: 2}} />
            ) : supervisorHandSummaryError ? (
              <Alert severity="error" sx={{mt: 2}}>Could not load supervisor hand data.</Alert>
            ) : supervisorHandSummary.length === 0 ? (
              <Typography sx={{mt: 2}}>No farm supervisors found.</Typography>
            ) : (
              <List disablePadding sx={{mt: 1}}>
                {supervisorHandSummary.map(({id, name, handCount}) => (
                  <ListItem key={id} divider disableGutters sx={{gap: 2}}>
                    <Typography sx={{flex: 1}}>{name}</Typography>
                    <Typography aria-label={`${handCount} hands have in-progress field jobs`}>
                      {handCount}
                    </Typography>
                  </ListItem>
                ))}
              </List>
            )}
          </CardContent>
        </Card>
      </Box>
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
          <FarmsDataGrid onSuccess={handleGridSuccess} />
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
          <EquipmentsDataGrid onSuccess={handleGridSuccess} />
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
          <FieldJobsDataGrid onSuccess={handleGridSuccess} />
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
          <ServiceReportsDataGrid onSuccess={handleGridSuccess} />
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
          <HandsDataGrid onSuccess={handleGridSuccess} />
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
          <SupervisorsDataGrid onSuccess={handleGridSuccess} />
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
              <UsersDataGrid onSuccess={handleGridSuccess}/>
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