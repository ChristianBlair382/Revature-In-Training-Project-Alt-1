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
]

export default function SupervisorsDataGrid({onSuccess}) {
    const [supervisors, setSupervisors] = useState([]);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const [dialogOpen, setDialogOpen] = useState(false);
    const [form_values, setFormValues] = useState({
        name: '',
    });

    async function fetchSupervisors() {
        setLoading(true)
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
    }

    const handleCreate = async() => {
        try {
            await apiClient.post('/supervisors', {
                ...form_values,
            });

            setDialogOpen(false);
            setFormValues({name: '',});
            onSuccess(`Supervisor "${form_values.name}" added successfully.`);
        } catch {

        }
    }

    if (loading) return <CircularProgress/>

    if (error) return <Alert severity="error">{error}</Alert>

    return (
        <Box>
            <Box>
                <DataGrid rows={supervisors} columns={columns} getRowId={(row) => row.id}/>
            </Box>
            <Button
            variant="outlined"
            sx={{mb: 2}}
            onClick={() => setDialogOpen(true)}
            >
                Add Supervisor
            </Button>
            <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
                <DialogTitle>Create New Supervisor</DialogTitle>
                <DialogContent>
                    <Stack spacing={2} sx={{mt: 1, minWidth: 300}}>
                        <TextField label="Name" value={form_values.name} onChange={handleFieldChange('name')}/>
                    </Stack>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
                    <Button variant="contained" onClick={handleCreate}>Add</Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
}