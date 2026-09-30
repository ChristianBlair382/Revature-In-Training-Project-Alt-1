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
    Stack,
    TextField
} from "@mui/material";
import apiClient from "../../api/client.js";

const columns = [
    {field: 'id', headerName: "ID", width: 70},
    {field: 'name', headerName: "Farm Name", width: 140},
    {field: 'location_region', headerName: "Location Region", width: 100},
    {field: 'capacity', headerName: "Capacity", width: 70, type: "number"},
    {field: 'supervisor_id', headerName: "Supervisor ID", width: 70, type: "number"},
]

export default function FarmsDataGrid({onSuccess}) {
    const [farms, setFarms] = useState([]);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const [dialogOpen, setDialogOpen] = useState(false);
    const [form_values, setFormValues] = useState({
        name: '',
        location_region: '',
        capacity: '',
        supervisor_id: '',
    });

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

    const handleCreate = async() => {
        try {
            await apiClient.post('/farms', {
                ...form_values,
                capacity: Number(form_values.capacity),
                supervisor_id: Number(form_values.supervisor_id),
            });

            setDialogOpen(false);
            setFormValues({name: '', location_region: '', capacity: '', supervisor_id: '',});
            onSuccess(`Farm ${form_values.name} created successfully.`);
        } catch {

        }
    }

    if (loading) return <CircularProgress/>

    if (error) return <Alert severity="error">{error}</Alert>

    return (
        <Box>
            <Box>
                <DataGrid rows={farms} columns={columns} getRowId={(row) => row.id}/>
            </Box>
            <Button
            variant="outlined"
            sx={{mb: 2}}
            onClick={() => setDialogOpen(true)}
            >
                Add Farm
            </Button>
            <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
                <DialogTitle>Create New Farm</DialogTitle>
                <DialogContent>
                    <Stack spacing={2} sx={{mt: 1, minWidth: 300}}>
                        <TextField label="Name" value={form_values.name} onChange={handleFieldChange('name')}/>
                        <TextField label="Location Region" value={form_values.location_region} onChange={handleFieldChange('location_region')}/>
                        <TextField label="Capacity" type="number" value={form_values.capacity} onChange={handleFieldChange('capacity')}/>
                        <TextField labal="Supervisor ID" type="number" value={form_values.supervisor_id} onChange={handleFieldChange('supervisor_id')}/>
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