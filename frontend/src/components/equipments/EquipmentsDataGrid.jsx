import { useEffect, useState } from "react";
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
    MenuItem,
    Stack,
    TextField
} from "@mui/material";
import apiClient from "../../api/client.js";

const columns = [
    {field: 'id', headerName: "ID", width: 70},
    {field: 'serial_num', headerName: "Serial Number", width: 140},
    {field: 'model', headerName: "Model", width: 100},
    {field: 'fuel_lvl', headerName: "Fuel Level", width: 70, type: "number"},
    {field: 'status', headerName: "Status", width: 70},
    {field: 'farm_id', headerName: "Farm ID", width: 70, type: "number"},
]

const STATUS_VALUES = ['Idle', 'In-Use', 'Maintenance', 'Retired']

export default function EquipmentsDataGrid({onSuccess}) {
    const [equipments, setEquipments] = useState([]);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const [dialogOpen, setDialogOpen] = useState(false);
    const [form_values, setFormValues] = useState({
        serial_num: '',
        model: '',
        fuel_lvl: '',
        status: 'Idle',
        farm_id: '',
    });

    async function fetchEquipments() {
        setLoading(true)
        try {
            const response = await apiClient.get('/equipments');
            setEquipments(response.data);
            setError(null);
        } catch {
            setError('Error: Could not load equipment data.');
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        fetchEquipments();
    }, []);

    const handleFieldChange = (field) => (event) => {
        setFormValues((prev) => ({...prev, [field]: event.target.value}));
    }

    const handleCreate = async() => {
        try {
            await apiClient.post('/equipments', {
                ...form_values,
                fuel_lvl: Number(form_values.fuel_lvl),
                farm_id_id: Number(form_values.farm_id),
            });

            setDialogOpen(false);
            setFormValues({serial_num: '', model: '', fuel_lvl: '', status: 'Idle', farm_id: '',});
            onSuccess(`Equipment ${form_values.serial_num} created successfully.`);
        } catch {

        }
    }

    if (loading) return <CircularProgress/>

    if (error) return <Alert severity="error">{error}</Alert>

    return (
        <Box>
            <Box>
                <DataGrid rows={equipments} columns={columns} getRowId={(row) => row.id}/>
            </Box>
            <Button
            variant="outlined"
            sx={{mb: 2}}
            onClick={() => setDialogOpen(true)}
            >
                Add Equipment
            </Button>
            <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
                <DialogTitle>Create New Equipment</DialogTitle>
                <DialogContent>
                    <Stack spacing={2} sx={{mt: 1, minWidth: 300}}>
                        <TextField label="Serial #" value={form_values.serial_num} onChange={handleFieldChange('serial_num')}/>
                        <TextField label="Model" value={form_values.model} onChange={handleFieldChange('model')}/>
                        <TextField label="Fuel Level" type="number" value={form_values.fuel_lvl} onChange={handleFieldChange('fuel_lvl')}/>
                        <TextField select label="Status" onChange={handleFieldChange('status')}>
                            {STATUS_VALUES.map((option) => (
                                <MenuItem key={option} value={option}>{option}</MenuItem>
                            ))}
                        </TextField>
                        <TextField labal="Farm ID" type="number" value={form_values.farm_id} onChange={handleFieldChange('farm_id')}/>
                    </Stack>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
                    <Button variant="contained" onClick={handleCreate}>Create</Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
}