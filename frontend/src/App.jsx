import {
  Container,
  Typography,
  Box,
  Button,
  Snackbar,
  Alert,
  Card,
  CardContent,
  CircularProgress,
  List,
  ListItem,
  ListItemIcon,
  ListItemButton,
  ListItemText,
  Drawer
} from "@mui/material";
import { useEffect, useMemo, useState } from "react";
import { CssBaseline, ThemeProvider, useMediaQuery } from "@mui/material";
import { AuthProvider, useAuth } from "./context/AuthContext.jsx";
import createAppTheme from "./theme.js";
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

import GridViewIcon from '@mui/icons-material/GridView';
import WarehouseIcon from '@mui/icons-material/Warehouse';
import PrecisionManufacturingIcon from '@mui/icons-material/PrecisionManufacturing';
import AssignmentIcon from '@mui/icons-material/Assignment';
import ReceiptLongIcon from '@mui/icons-material/ReceiptLong';
import GroupsIcon from '@mui/icons-material/Groups';
import EngineeringIcon from '@mui/icons-material/Engineering';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';

function Dashboard({mode, onToggleColorMode}) {
  const {user, logout} = useAuth()
  const [notification, setNotification] = useState('')
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [selectedPage, setSelectedPage] = useState('summaries')
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
  const toggleDrawer = (newOpen) => () => {
    setDrawerOpen(newOpen);
  };
  const displaySelectedPage = (string) => () => {
    setSelectedPage(string)
  }
  

  // DRAWER CONSTRUCT
  const DrawerList = (
    <Box sx={{ width: 300, height: "100%", display: "flex", flexDirection: "column", }} role="presentation" onClick={toggleDrawer(false)}>
      <List>
        <ListItem>
          <ListItemButton color="inherit" onClick={displaySelectedPage('summaries')}>
            <ListItemIcon color="secondary">
              <GridViewIcon />
            </ListItemIcon>
            <ListItemText primary="Dashboard"/>
          </ListItemButton>
        </ListItem>
        <ListItem>
          <ListItemButton color="inherit" onClick={displaySelectedPage('farms')}>
            <ListItemIcon color="secondary">
              <WarehouseIcon />
            </ListItemIcon>
            <ListItemText primary="Farms"/>
          </ListItemButton>
        </ListItem>
        <ListItem>
          <ListItemButton color="inherit" onClick={displaySelectedPage('equipments')}>
            <ListItemIcon color="secondary">
              <PrecisionManufacturingIcon />
            </ListItemIcon>
            <ListItemText primary="Equipments"/>
          </ListItemButton>
        </ListItem>
        <ListItem>
          <ListItemButton color="inherit" onClick={displaySelectedPage('field_jobs')}>
            <ListItemIcon color="secondary">
              <AssignmentIcon />
            </ListItemIcon>
            <ListItemText primary="Field Jobs"/>
          </ListItemButton>
        </ListItem>
        <ListItem>
          <ListItemButton color="inherit" onClick={displaySelectedPage('service_reports')}>
            <ListItemIcon color="secondary">
              <ReceiptLongIcon />
            </ListItemIcon>
            <ListItemText primary="Service Reports"/>
          </ListItemButton>
        </ListItem>
        <ListItem>
          <ListItemButton color="inherit" onClick={displaySelectedPage('hands')}>
            <ListItemIcon color="secondary">
              <GroupsIcon />
            </ListItemIcon>
            <ListItemText primary="Hands"/>
          </ListItemButton>
        </ListItem>
        <ListItem>
          <ListItemButton color="inherit" onClick={displaySelectedPage('supervisors')}>
            <ListItemIcon color="secondary">
              <EngineeringIcon />
            </ListItemIcon>
            <ListItemText primary="Supervisors"/>
          </ListItemButton>
        </ListItem>
        { isFOA && (
          <>
            <ListItem>
              <ListItemButton color="inherit" onClick={displaySelectedPage('users')}>
                <ListItemIcon color="secondary">
                  <AccountCircleIcon />
                </ListItemIcon>
                <ListItemText primary="Users"/>
              </ListItemButton>
            </ListItem>
          </>
        )}
      </List>
      <Box 
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'flex-center',
          mt: 'auto'
        }}
      >
        <Typography sx={{ mr: 2 }}>{user?.sub} </Typography>
        <Typography sx={{ fontSize: 10 }}>{user?.role}</Typography>
        <Button color="inherit" onClick={logout}>Log Out</Button>
      </Box>
    </Box>
  );

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
      <AppHeader
        onDrawerClick={toggleDrawer(true)}
        mode={mode}
        onToggleColorMode={onToggleColorMode}
      />
      <Drawer open={drawerOpen} onClose={toggleDrawer(false)}>
        {DrawerList}
      </Drawer>
      {selectedPage === 'summaries' && (
        <Box sx={{display: 'grid', gridTemplateColumns: {xs: '1fr', md: 'repeat(3, minmax(0, 1fr))'}, gap: 2, px: 3, py: 2, padding: 4}}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="h6" component="h2">
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
              <Typography variant="h6" component="h2">
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
              <Typography variant="h6" component="h2">
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
      )}
      <Container sx={{ padding: 4 }}>
        { selectedPage === 'farms' && (
          <>
            <Typography
              variant="h5"
              component="h2"
              gutterBottom
            >
              Farms
            </Typography>
            <Box sx={{mb: 4}}>
              <FarmsDataGrid onSuccess={handleGridSuccess} />
            </Box>
          </>
        )}
        { selectedPage === 'equipments' && (
          <>
            <Typography
            variant="h5"
            component="h2"
            gutterBottom
            >
              Equipments
            </Typography>
            <Box sx={{mb: 4}}>
              <EquipmentsDataGrid onSuccess={handleGridSuccess} />
            </Box>
          </>
        )}
        { selectedPage === 'field_jobs' && (
          <>
            <Typography
              variant="h5"
              component="h2"
              gutterBottom
            >
              Field Jobs
            </Typography>
            <Box sx={{mb: 4}}>
              <FieldJobsDataGrid onSuccess={handleGridSuccess} />
            </Box>
          </>
        )}
        { selectedPage === 'service_reports' && (
          <>
            <Typography
              variant="h5"
              component="h2"
              gutterBottom
            >
              Service Reports
            </Typography>
            <Box sx={{mb: 4}}>
              <ServiceReportsDataGrid onSuccess={handleGridSuccess} />
            </Box>
          </>
        )}
        { selectedPage === 'hands' && (
          <>
            <Typography
              variant="h5"
              component="h2"
              gutterBottom
            >
              Hands
            </Typography>
            <Box sx={{mb: 4}}>
              <HandsDataGrid onSuccess={handleGridSuccess} />
            </Box>
          </>
        )}
        { selectedPage === 'supervisors' && (
          <>
            <Typography
              variant="h5"
              component="h2"
              gutterBottom
            >
              Supervisors
            </Typography>
            <Box sx={{mb: 4}}>
              <SupervisorsDataGrid onSuccess={handleGridSuccess} />
            </Box>
          </>
        )}
        { isFOA && selectedPage === 'users' && 
          <>
            <Typography
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

function AppContent({mode, onToggleColorMode}) {
  const {isAuthenticated} = useAuth();
  return isAuthenticated
    ? <Dashboard mode={mode} onToggleColorMode={onToggleColorMode} />
    : (
      <>
        <AppHeader mode={mode} onToggleColorMode={onToggleColorMode} />
        <LoginForm />
      </>
    );
}

function App() {
  const [colorModePreference, setColorModePreference] = useState(() => {
    try {
      const savedPreference = localStorage.getItem("agricoreColorMode");
      return savedPreference === "light" || savedPreference === "dark" ? savedPreference : "system";
    } catch (error) {
      console.warn("Could not read the saved color preference; Defaulting to system theme settings...", error);
      return "system";
    }
  });
  const prefersDarkMode = useMediaQuery("(prefers-color-scheme: dark)");
  const mode = colorModePreference === "system" ? (prefersDarkMode ? "dark" : "light") : colorModePreference;
  const theme = useMemo(() => createAppTheme(mode), [mode]);

  useEffect(() => {
    try {
      window.localStorage.setItem('agricoreColorMode', colorModePreference)
    } catch (error) {
      console.warn("Could not save current color preference; will not remain persistent after this session. Sorry!", error);
    }
    document.documentElement.dataset.colorMode = mode;
  }, [mode]);

  const toggleColorMode = () => {
    setColorModePreference(mode === "dark" ? "light" : "dark");
  };

  useEffect(() => {
    function handleKeyShortcut(e){
      const isCtrlOrCmd = e.ctrlKey || e.metaKey
      if (isCtrlOrCmd && e.key === "."){
        e.preventDefault();
        toggleColorMode();
      }
    }
    window.addEventListener("keydown", handleKeyShortcut);
    return () => window.removeEventListener("keydown", handleKeyShortcut);
  }, [toggleColorMode]);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <AppContent mode={mode} onToggleColorMode={toggleColorMode} />
      </AuthProvider>
    </ThemeProvider>
  )
}

export default App