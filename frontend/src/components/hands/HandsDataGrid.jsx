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
    TextField,
    MenuItem
} from "@mui/material";
import apiClient from "../../api/client.js";
import { useAuth } from "../../context/AuthContext.jsx";

const EMPTY_FORM_VALUES = {
    name: '',
    farm_id: '',
};

export default function HandDataGrid({onSuccess}) {
    const {user} = useAuth();
    const isAdmin = user?.role === 'Field_Operations_Admin' || user?.role === 'FOA';
    const [hands, setHands] = useState([]);
    const [farms, setFarms] = useState([]);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const [dialogOpen, setDialogOpen] = useState(false);
    const [manageDialogOpen, setManageDialogOpen] = useState(false);
    const [selectedHand, setSelectedHand] = useState(null);
    const [deleteConfirmation, setDeleteConfirmation] = useState(false);
    const [actionError, setActionError] = useState(null);
    const [saving, setSaving] = useState(false);
    const [form_values, setFormValues] = useState({...EMPTY_FORM_VALUES});

    async function fetchHands() {
        setLoading(true);
        try {
            const [handResponse, farmResponse] = await Promise.all([
                apiClient.get('/hands'),
                apiClient.get('/farms'),
            ]);
            setHands(handResponse.data);
            setFarms(farmResponse.data);
            setError(null);
        } catch {
            setError('Error: Could not load hand anf farm data.');
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        fetchHands();
    }, []);

    const handleFieldChange = (field) => (event) => {
        setFormValues((prev) => ({...prev, [field]: event.target.value}));
    };

    const openManageDialog = useCallback((hand) => {
        setSelectedHand(hand);
        setFormValues({
            name: hand.name,
            farm_id: hand.farm_id,
        });
        setDeleteConfirmation(false);
        setActionError(null);
        setManageDialogOpen(true);
    }, []);

    const farmsById = useMemo(() => new Map(
        farms.map((farm) => [farm.id, farm.name])
    ), [farms]);

    const columns = useMemo(() => [
        {field: 'id', headerName: "ID", width: 70},
        {field: 'name', headerName: "Hand Name", width: 140},
        {
            field: 'farm_id',
            headerName: "Farm",
            width: 160,
            valueGetter: (_value, row) => farmsById.get(row.farm_id) ?? `Unknown farm (${row.farm_id})`,
        },
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
    ], [isAdmin, farmsById, openManageDialog]);

    const handleCreate = async() => {
        setActionError(null);
        try {
            await apiClient.post('/hands', {
                ...form_values,
                farm_id: Number(form_values.farm_id),
            });

            setDialogOpen(false);
            setFormValues({...EMPTY_FORM_VALUES});
            onSuccess(`Hand "${form_values.name}" created successfully.`);
            await fetchHands();
        } catch {
            setActionError('Could not create hand. Check the values and try again.');
        }
    };

    const handleUpdate = async() => {
        if (!selectedHand) return;

        setSaving(true);
        setActionError(null);
        try {
            const response = await apiClient.patch(`/hands/${selectedHand.id}`, {
                ...form_values,
                farm_id: Number(form_values.farm_id),
            });
            setHands((currentHands) => currentHands.map((hand) => (
                hand.id === selectedHand.id ? response.data : hand
            )));
            setManageDialogOpen(false);
            onSuccess(`Hand ${response.data.name} updated successfully.`);
        } catch {
            setActionError('Could not update hand. Check the values and try again.');
        } finally {
            setSaving(false);
        }
    };

    const handleDelete = async() => {
        if (!selectedHand) return;

        setSaving(true);
        setActionError(null);
        try {
            await apiClient.delete(`/hands/${selectedHand.id}`);
            setHands((currentHands) => currentHands.filter((hand) => hand.id !== selectedHand.id));
            setManageDialogOpen(false);
            onSuccess(`Hand ${selectedHand.name} deleted successfully.`);
        } catch {
            setActionError('Could not delete hand. It may still be in use.');
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
                    rows={hands} 
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
                    Add Hand
                </Button>
            )}
            <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
                <DialogTitle>Create New Hand</DialogTitle>
                <DialogContent>
                    <Stack spacing={2} sx={{mt: 1, minWidth: 300}}>
                        {actionError && <Alert severity="error">{actionError}</Alert>}
                        <TextField label="Name" value={form_values.name} onChange={handleFieldChange('name')}/>
                        <TextField
                            select
                            label="Farm"
                            value={form_values.farm_id}
                            onChange={handleFieldChange('farm_id')}
                        >
                            {farms.length > 0 ? farms.map((farm) => (
                                <MenuItem key={farm.id} value={farm.id}>{farm.name}</MenuItem>
                            )) : (
                                <MenuItem value="" disabled>No farms available</MenuItem>
                            )}
                        </TextField>
                    </Stack>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
                    <Button 
                        variant="contained" 
                        onClick={handleCreate}
                        disabled={!form_values.farm_id || farms.length === 0}
                    >
                        Create
                    </Button>
                </DialogActions>
            </Dialog>
            <Dialog
                open={manageDialogOpen}
                onClose={() => !saving && setManageDialogOpen(false)}
            >
                <DialogTitle>
                    {deleteConfirmation ? 'Delete Hand?' : `Manage Hand ${selectedHand?.id ?? ''}`}
                </DialogTitle>
                <DialogContent>
                    <Stack spacing={2} sx={{mt: 1, minWidth: 300}}>
                        {actionError && <Alert severity="error">{actionError}</Alert>}
                        {deleteConfirmation ? (
                            <Alert severity="warning">
                                Delete {selectedHand?.name}? This action cannot be undone.
                            </Alert>
                        ) : (
                            <>
                                <TextField label="Name" value={form_values.name} onChange={handleFieldChange('name')}/>
                                <TextField
                                    select
                                    label="Farm"
                                    value={form_values.farm_id}
                                    onChange={handleFieldChange('farm_id')}
                                >
                                    {farms.length > 0 ? farms.map((farm) => (
                                        <MenuItem key={farm.id} value={farm.id}>{farm.name}</MenuItem>
                                    )) : (
                                        <MenuItem value="" disabled>No farms available</MenuItem>
                                    )}
                                </TextField>
                            </>
                        )}
                    </Stack>
                </DialogContent>
                <DialogActions>
                    {deleteConfirmation ? (
                        <>
                            <Button onClick={() => setDeleteConfirmation(false)} disabled={saving}>Keep Hand</Button>
                            <Button color="error" variant="contained" onClick={handleDelete} disabled={saving}>
                                Delete Hand
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