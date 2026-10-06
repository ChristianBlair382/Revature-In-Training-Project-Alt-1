import { useCallback, useEffect, useMemo, useState } from "react";
import { DataGrid } from "@mui/x-data-grid";
import {
    Alert,
    Box,
    Chip,
    CircularProgress,
    Button,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    MenuItem,
    Stack,
    TextField
} from "@mui/material";
import apiClient from "../../api/client.js";
import { useAuth } from "../../context/AuthContext.jsx";

const EMPTY_FORM_VALUES = {
    serial_num: '',
    model: '',
    fuel_lvl: '',
    status: 'Idle',
    farm_id: '',
};

const STATUS_VALUES = ['Idle', 'In-Use', 'Maintenance', 'Retired'];

export default function EquipmentsDataGrid({onSuccess}) {
    const {user} = useAuth();
    const isAdmin = user?.role === 'Field_Operations_Admin' || user?.role === 'FOA';
    const isFieldHand = user?.role === 'Field_Hand' || user?.role === 'FH';
    const canManage = isAdmin || isFieldHand;
    const [equipments, setEquipments] = useState([]);
    const [farms, setFarms] = useState([]);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const [dialogOpen, setDialogOpen] = useState(false);
    const [manageDialogOpen, setManageDialogOpen] = useState(false);
    const [selectedEquipment, setSelectedEquipment] = useState(null);
    const [deleteConfirmation, setDeleteConfirmation] = useState(false);
    const [actionError, setActionError] = useState(null);
    const [saving, setSaving] = useState(false);
    const [form_values, setFormValues] = useState({...EMPTY_FORM_VALUES});

    async function fetchEquipments() {
        setLoading(true);
        try {
            const [equipmentResponse, farmResponse] = await Promise.all([
                apiClient.get('/equipments'),
                apiClient.get('/farms'),
            ]);
            setEquipments(equipmentResponse.data);
            setFarms(farmResponse.data);
            setError(null);
        } catch {
            setError('Error: Could not load equipment and farm data.');
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        fetchEquipments();
    }, []);

    const handleFieldChange = (field) => (event) => {
        setFormValues((prev) => ({...prev, [field]: event.target.value}));
    };

    const openManageDialog = useCallback((equipment) => {
        setSelectedEquipment(equipment);
        setFormValues({
            serial_num: equipment.serial_num,
            model: equipment.model,
            fuel_lvl: equipment.fuel_lvl,
            status: equipment.status,
            farm_id: equipment.farm_id,
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
        {field: 'serial_num', headerName: "Serial Number", width: 140},
        {field: 'model', headerName: "Model", width: 100},
        {
            field: 'fuel_lvl',
            headerName: "Fuel Level",
            width: 90,
            type: "number",
            renderCell: ({value}) => `${value}%`,
        },
        {
            field: 'fuel_alert',
            headerName: 'Fuel Alert',
            width: 120,
            type: 'boolean',
            valueGetter: (_value, row) => row.low_fuel,
            renderCell: ({value}) => {
                return (
                    <Chip
                        label={value ? 'Low Fuel' : 'OK'}
                        color={value ? 'error' : 'success'}
                        variant={value ? 'filled' : 'outlined'}
                        size="small"
                    />
                );
            },
        },
        {field: 'status', headerName: "Status", width: 70},
        {
            field: 'farm_id',
            headerName: "Farm",
            width: 160,
            valueGetter: (_value, row) => farmsById.get(row.farm_id) ?? `Unknown farm (${row.farm_id})`,
        },
        ...(canManage ? [{
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
    ], [canManage, farmsById, openManageDialog]);

    const handleCreate = async() => {
        setActionError(null);
        try {
            await apiClient.post('/equipments', {
                ...form_values,
                fuel_lvl: Number(form_values.fuel_lvl),
                farm_id: Number(form_values.farm_id),
            });

            setDialogOpen(false);
            setFormValues({...EMPTY_FORM_VALUES});
            onSuccess(`Equipment "${form_values.serial_num}" created successfully.`);
            await fetchEquipments();
        } catch {
            setActionError('Could not create equipment. Check the values and try again.');
        }
    };

    const handleUpdate = async() => {
        if (!selectedEquipment) return;

        setSaving(true);
        setActionError(null);
        try {
            let response;

            if (isFieldHand) {
                response = await apiClient.patch(`/equipments/${selectedEquipment.id}/status`, {
                    status: form_values.status,
                });
            } else {
                response = await apiClient.patch(`/equipments/${selectedEquipment.id}`, {
                    ...form_values,
                    fuel_lvl: Number(form_values.fuel_lvl),
                    farm_id: Number(form_values.farm_id),
                });
            }

            setEquipments((currentEquipments) => currentEquipments.map((equipment) => (
                equipment.id === selectedEquipment.id ? { ...equipment, ...response.data } : equipment
            )));
            setManageDialogOpen(false);
            onSuccess(`Equipment ${response.data.serial_num} updated successfully.`);
        } catch {
            setActionError('Could not update equipment. Check the values and try again.');
        } finally {
            setSaving(false);
        }
    };

    const handleDelete = async() => {
        if (!selectedEquipment) return;

        setSaving(true);
        setActionError(null);
        try {
            await apiClient.delete(`/equipments/${selectedEquipment.id}`);
            setEquipments((currentEquipments) => currentEquipments.filter((equipment) => equipment.id !== selectedEquipment.id));
            setManageDialogOpen(false);
            onSuccess(`Equipment ${selectedEquipment.serial_num} deleted successfully.`);
        } catch {
            setActionError('Could not delete equipment. It may still be in use.');
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
                    rows={equipments} 
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
                    Add Equipment
                </Button>
            )}
            <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
                <DialogTitle>Create New Equipment</DialogTitle>
                <DialogContent>
                    <Stack spacing={2} sx={{mt: 1, minWidth: 300}}>
                        {actionError && <Alert severity="error">{actionError}</Alert>}
                        <TextField label="Serial #" value={form_values.serial_num} onChange={handleFieldChange('serial_num')}/>
                        <TextField label="Model" value={form_values.model} onChange={handleFieldChange('model')}/>
                        <TextField label="Fuel Level" type="number" value={form_values.fuel_lvl} onChange={handleFieldChange('fuel_lvl')}/>
                        <TextField select label="Status" value={form_values.status} onChange={handleFieldChange('status')}>
                            {STATUS_VALUES.map((option) => (
                                <MenuItem key={option} value={option}>{option}</MenuItem>
                            ))}
                        </TextField>
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
                    {deleteConfirmation ? 'Delete Equipment?' : `${isFieldHand ? 'Update' : 'Manage'} Equipment ${selectedEquipment?.id ?? ''}`}
                </DialogTitle>
                <DialogContent>
                    <Stack spacing={2} sx={{mt: 1, minWidth: 300}}>
                        {actionError && <Alert severity="error">{actionError}</Alert>}
                        {deleteConfirmation ? (
                            <Alert severity="warning">
                                Delete {selectedEquipment?.serial_num}? This action cannot be undone.
                            </Alert>
                        ) : (
                            <>
                                {isFieldHand ? (
                                    <TextField select label="Status" value={form_values.status} onChange={handleFieldChange('status')}>
                                        {STATUS_VALUES.map((option) => (
                                            <MenuItem key={option} value={option}>{option}</MenuItem>
                                        ))}
                                    </TextField>
                                ) : (
                                    <>
                                        <TextField label="Serial #" value={form_values.serial_num} onChange={handleFieldChange('serial_num')}/>
                                        <TextField label="Model" value={form_values.model} onChange={handleFieldChange('model')}/>
                                        <TextField label="Fuel Level" type="number" value={form_values.fuel_lvl} onChange={handleFieldChange('fuel_lvl')}/>
                                        <TextField select label="Status" value={form_values.status} onChange={handleFieldChange('status')}>
                                            {STATUS_VALUES.map((option) => (
                                                <MenuItem key={option} value={option}>{option}</MenuItem>
                                            ))}
                                        </TextField>
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
                            </>
                        )}
                    </Stack>
                </DialogContent>
                <DialogActions>
                    {deleteConfirmation ? (
                        <>
                            <Button onClick={() => setDeleteConfirmation(false)} disabled={saving}>Keep Equipment</Button>
                            <Button color="error" variant="contained" onClick={handleDelete} disabled={saving}>
                                Delete Equipment
                            </Button>
                        </>
                    ) : (
                        <>
                            <Button onClick={() => setManageDialogOpen(false)} disabled={saving}>Cancel</Button>
                            {!isFieldHand && (
                                <Button color="error" onClick={() => setDeleteConfirmation(true)} disabled={saving}>
                                    Delete
                                </Button>
                            )}
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