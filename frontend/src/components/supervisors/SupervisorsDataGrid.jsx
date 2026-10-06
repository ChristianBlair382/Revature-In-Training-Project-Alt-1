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
};

export default function SupervisorsDataGrid({onSuccess}) {
    const {user} = useAuth();
    const isAdmin = user?.role === 'Field_Operations_Admin' || user?.role === 'FOA';
    const [supervisors, setSupervisors] = useState([]);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const [dialogOpen, setDialogOpen] = useState(false);
    const [manageDialogOpen, setManageDialogOpen] = useState(false);
    const [selectedSupervisor, setSelectedSupervisor] = useState(null);
    const [deleteConfirmation, setDeleteConfirmation] = useState(false);
    const [actionError, setActionError] = useState(null);
    const [saving, setSaving] = useState(false);
    const [form_values, setFormValues] = useState({...EMPTY_FORM_VALUES});

    async function fetchSupervisors() {
        setLoading(true);
        try {
            const response = await apiClient.get('/supervisors');
            setSupervisors(response.data);
            setError(null);
        } catch {
            setError('Error: Could not load supervisor data.');
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        fetchSupervisors();
    }, []);

    const handleFieldChange = (field) => (event) => {
        setFormValues((prev) => ({...prev, [field]: event.target.value}));
    };

    const openManageDialog = useCallback((supervisor) => {
        setSelectedSupervisor(supervisor);
        setFormValues({
            name: supervisor.name,
        });
        setDeleteConfirmation(false);
        setActionError(null);
        setManageDialogOpen(true);
    }, []);

    const columns = useMemo(() => [
        {field: 'id', headerName: "ID", width: 70},
        {field: 'name', headerName: "Supervisor Name", width: 140},
        ...(isAdmin ? [{
            field: 'actions',
            headerName: 'Actions',
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
            await apiClient.post('/supervisors', {
                ...form_values,
            });

            setDialogOpen(false);
            setFormValues({...EMPTY_FORM_VALUES});
            onSuccess(`Supervisor "${form_values.name}" created successfully.`);
            await fetchSupervisors();
        } catch {
            setActionError('Could not create supervisor. Check the values and try again.');
        }
    };

    const handleUpdate = async() => {
        if (!selectedSupervisor) return;

        setSaving(true);
        setActionError(null);
        try {
            const response = await apiClient.patch(`/supervisors/${selectedSupervisor.id}`, {
                ...form_values,
            });
            setSupervisors((currentSupervisors) => currentSupervisors.map((supervisor) => (
                supervisor.id === selectedSupervisor.id ? response.data : supervisor
            )));
            setManageDialogOpen(false);
            onSuccess(`Supervisor ${response.data.name} updated successfully.`);
        } catch {
            setActionError('Could not update supervisor. Check the values and try again.');
        } finally {
            setSaving(false);
        }
    };

    const handleDelete = async() => {
        if (!selectedSupervisor) return;

        setSaving(true);
        setActionError(null);
        try {
            await apiClient.delete(`/supervisors/${selectedSupervisor.id}`);
            setSupervisors((currentSupervisors) => currentSupervisors.filter((supervisor) => supervisor.id !== selectedSupervisor.id));
            setManageDialogOpen(false);
            onSuccess(`Supervisor ${selectedSupervisor.name} deleted successfully.`);
        } catch {
            setActionError('Could not delete supervisor. It may still be in use.');
        } finally {
            setSaving(false);
        }
    };

    const openCreateDialog = () => {
        setFormValues({...EMPTY_FORM_VALUES});
        setActionError(null);
        setDialogOpen(true);
    };

    if (loading) return <CircularProgress/>;

    if (error) return <Alert severity="error">{error}</Alert>;

    return (
        <Box>
            <Box>
                <DataGrid 
                    rows={supervisors}
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
                    Add Supervisor
                </Button>
            )}
            <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
                <DialogTitle>Create New Supervisor</DialogTitle>
                <DialogContent>
                    <Stack spacing={2} sx={{mt: 1, minWidth: 300}}>
                        {actionError && <Alert severity="error">{actionError}</Alert>}
                        <TextField label="Name" value={form_values.name} onChange={handleFieldChange('name')}/>
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
                    {deleteConfirmation ? 'Delete Supervisor?' : `Manage Supervisor ${selectedSupervisor?.id ?? ''}`}
                </DialogTitle>
                <DialogContent>
                    <Stack spacing={2} sx={{mt: 1, minWidth: 300}}>
                        {actionError && <Alert severity="error">{actionError}</Alert>}
                        {deleteConfirmation ? (
                            <Alert severity="warning">
                                Delete {selectedSupervisor?.name}? This action cannot be undone.
                            </Alert>
                        ) : (
                            <TextField label="Name" value={form_values.name} onChange={handleFieldChange('name')}/>
                        )}
                    </Stack>
                </DialogContent>
                <DialogActions>
                    {deleteConfirmation ? (
                        <>
                            <Button onClick={() => setDeleteConfirmation(false)} disabled={saving}>Keep Supervisor</Button>
                            <Button color="error" variant="contained" onClick={handleDelete} disabled={saving}>
                                Delete Supervisor
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