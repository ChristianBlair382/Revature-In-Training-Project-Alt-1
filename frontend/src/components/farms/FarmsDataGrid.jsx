import { useCallback, useEffect, useMemo, useState } from "react";
import { DataGrid } from "@mui/x-data-grid";
import {
    Alert,
    Box,
    CircularProgress,
    Button,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    Stack,
    TextField
} from "@mui/material";
import apiClient from "../../api/client.js";
import { useAuth } from "../../context/AuthContext.jsx";

const EMPTY_FORM_VALUES = {
    name: '',
    location_region: '',
    capacity: '',
    supervisor_id: '',
};

export default function FarmsDataGrid({onSuccess}) {
    const {user} = useAuth();
    const isAdmin = user?.role === 'Field_Operations_Admin' || user?.role === 'FOA';
    const [farms, setFarms] = useState([]);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const [dialogOpen, setDialogOpen] = useState(false);
    const [manageDialogOpen, setManageDialogOpen] = useState(false);
    const [selectedFarm, setSelectedFarm] = useState(null);
    const [deleteConfirmation, setDeleteConfirmation] = useState(false);
    const [actionError, setActionError] = useState(null);
    const [saving, setSaving] = useState(false);
    const [form_values, setFormValues] = useState({...EMPTY_FORM_VALUES});

    async function fetchFarms() {
        setLoading(true)
        try {
            const response = await apiClient.get('/farms');
            setFarms(response.data);
            setError(null);
        } catch {
            setError('Error: Could not load farm data.');
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        fetchFarms();
    }, []);

    const handleFieldChange = (field) => (event) => {
        setFormValues((prev) => ({...prev, [field]: event.target.value}));
    }

    const openManageDialog = useCallback((farm) => {
        setSelectedFarm(farm);
        setFormValues({
            name: farm.name,
            location_region: farm.location_region,
            capacity: farm.capacity,
            supervisor_id: farm.supervisor_id,
        });
        setDeleteConfirmation(false);
        setActionError(null);
        setManageDialogOpen(true);
    }, []);

    const columns = useMemo(() => [
        {field: 'id', headerName: "ID", width: 70},
        {field: 'name', headerName: "Farm Name", width: 140},
        {field: 'location_region', headerName: "Location Region", width: 140},
        {field: 'capacity', headerName: "Capacity", width: 90, type: "number"},
        {field: 'supervisor_id', headerName: "Supervisor ID", width: 110, type: "number"},
        ...(isAdmin ? [{
            field: 'actions',
            headerName: "Actions",
            width: 120,
            sortable: false,
            filterable: false,
            renderCell: ({row}) => (
                <Button size="small" onClick={() => openManageDialog(row)}>
                    Manage
                </Button>
            ),
        }] : []),
    ], [isAdmin, openManageDialog]);

    const handleCreate = async() => {
        setActionError(null);
        try {
            await apiClient.post('/farms', {
                ...form_values,
                capacity: Number(form_values.capacity),
                supervisor_id: Number(form_values.supervisor_id),
            });

            setDialogOpen(false);
            setFormValues({...EMPTY_FORM_VALUES});
            onSuccess(`Farm "${form_values.name}" created successfully.`);
            await fetchFarms();
        } catch {
            setActionError('Could not create farm. Check the values and try again.');
        }
    }

    const handleUpdate = async() => {
        if (!selectedFarm) return;

        setSaving(true);
        setActionError(null);
        try {
            const response = await apiClient.patch(`/farms/${selectedFarm.id}`, {
                ...form_values,
                capacity: Number(form_values.capacity),
                supervisor_id: Number(form_values.supervisor_id),
            });
            setFarms((currentFarms) => currentFarms.map((farm) => (
                farm.id === selectedFarm.id ? response.data : farm
            )));
            setManageDialogOpen(false);
            onSuccess(`Farm ${response.data.name} updated successfully.`);
        } catch {
            setActionError('Could not update farm. Check the values and try again.');
        } finally {
            setSaving(false);
        }
    }

    const handleDelete = async() => {
        if (!selectedFarm) return;

        setSaving(true);
        setActionError(null);
        try {
            await apiClient.delete(`/farms/${selectedFarm.id}`);
            setFarms((currentFarms) => currentFarms.filter((farm) => farm.id !== selectedFarm.id));
            setManageDialogOpen(false);
            onSuccess(`Farm ${selectedFarm.name} deleted successfully.`);
        } catch {
            setActionError('Could not delete farm. It may still be in use.');
        } finally {
            setSaving(false);
        }
    }

    const openCreateDialog = () => {
        setFormValues({...EMPTY_FORM_VALUES});
        setActionError(null);
        setDialogOpen(true);
    }

    if (loading) return <CircularProgress/>

    if (error) return <Alert severity="error">{error}</Alert>

    return (
        <Box>
            <Box>
                <DataGrid 
                    rows={farms} 
                    columns={columns} 
                    getRowId={(row) => row.id}
                    initialState={{
                        pagination: {
                            paginationModel: {
                                pageSize: 5,
                            },
                        },
                    }}
                />
            </Box>
            {isAdmin && (
                <Button
                    variant="outlined"
                    sx={{mb: 2}}
                    onClick={openCreateDialog}
                >
                    Add Farm
                </Button>
            )}
            <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
                <DialogTitle>Create New Farm</DialogTitle>
                <DialogContent>
                    <Stack spacing={2} sx={{mt: 1, minWidth: 300}}>
                        {actionError && <Alert severity="error">{actionError}</Alert>}
                        <TextField label="Name" value={form_values.name} onChange={handleFieldChange('name')}/>
                        <TextField label="Location Region" value={form_values.location_region} onChange={handleFieldChange('location_region')}/>
                        <TextField label="Capacity" type="number" value={form_values.capacity} onChange={handleFieldChange('capacity')}/>
                        <TextField label="Supervisor ID" type="number" value={form_values.supervisor_id} onChange={handleFieldChange('supervisor_id')}/>
                    </Stack>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
                    <Button variant="contained" onClick={handleCreate}>Create</Button>
                </DialogActions>
            </Dialog>
            <Dialog
                open={manageDialogOpen}
                onClose={() => !saving && setManageDialogOpen(false)}
            >
                <DialogTitle>
                    {deleteConfirmation ? 'Delete Farm?' : `Manage Farm ${selectedFarm?.id ?? ''}`}
                </DialogTitle>
                <DialogContent>
                    <Stack spacing={2} sx={{mt: 1, minWidth: 300}}>
                        {actionError && <Alert severity="error">{actionError}</Alert>}
                        {deleteConfirmation ? (
                            <Alert severity="warning">
                                Delete {selectedFarm?.name}? This action cannot be undone.
                            </Alert>
                        ) : (
                            <>
                                <TextField label="Name" value={form_values.name} onChange={handleFieldChange('name')}/>
                                <TextField label="Location Region" value={form_values.location_region} onChange={handleFieldChange('location_region')}/>
                                <TextField label="Capacity" type="number" value={form_values.capacity} onChange={handleFieldChange('capacity')}/>
                                <TextField label="Supervisor ID" type="number" value={form_values.supervisor_id} onChange={handleFieldChange('supervisor_id')}/>
                            </>
                        )}
                    </Stack>
                </DialogContent>
                <DialogActions>
                    {deleteConfirmation ? (
                        <>
                            <Button onClick={() => setDeleteConfirmation(false)} disabled={saving}>Keep Farm</Button>
                            <Button color="error" variant="contained" onClick={handleDelete} disabled={saving}>
                                Delete Farm
                            </Button>
                        </>
                    ) : (
                        <>
                            <Button onClick={() => setManageDialogOpen(false)} disabled={saving}>Cancel</Button>
                            <Button color="error" onClick={() => setDeleteConfirmation(true)} disabled={saving}>
                                Delete
                            </Button>
                            <Button variant="contained" onClick={handleUpdate} disabled={saving}>
                                Save Changes
                            </Button>
                        </>
                    )}
                </DialogActions>
            </Dialog>
        </Box>
    );
}