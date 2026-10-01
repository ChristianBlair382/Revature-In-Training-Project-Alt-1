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
    {field: 'farm_id', headerName: "Farm ID", width: 70, type: "number"},
]

export default function HandDataGrid({onSuccess}) {
    const [hands, setHands] = useState([]);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const [dialogOpen, setDialogOpen] = useState(false);
    const [form_values, setFormValues] = useState({
        name: '',
        farm_id: '',
    });

    async function fetchHands() {
        setLoading(true)
        try {
            const response = await apiClient.get('/hands');
            setHands(response.data);
            setError(null);
        } catch {
            setError('Error: Could not load hand data.');
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        fetchHands();
    }, []);

    const handleFieldChange = (field) => (event) => {
        setFormValues((prev) => ({...prev, [field]: event.target.value}));
    }

    const handleCreate = async() => {
        try {
            await apiClient.post('/hands', {
                ...form_values,
                farm_id: Number(form_values.farm_id),
            });

            setDialogOpen(false);
            setFormValues({name: '', farm_id: '',});
            onSuccess(`Hand "${form_values.name}" added successfully.`);
        } catch {

        }
    }

    if (loading) return <CircularProgress/>

    if (error) return <Alert severity="error">{error}</Alert>

    return (
        <Box>
            <Box>
                <DataGrid rows={hands} columns={columns} getRowId={(row) => row.id}/>
            </Box>
            <Button
            variant="outlined"
            sx={{mb: 2}}
            onClick={() => setDialogOpen(true)}
            >
                Add Hand
            </Button>
            <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
                <DialogTitle>Create New Hand</DialogTitle>
                <DialogContent>
                    <Stack spacing={2} sx={{mt: 1, minWidth: 300}}>
                        <TextField label="Name" value={form_values.name} onChange={handleFieldChange('name')}/>
                        <TextField labal="Farm ID" type="number" value={form_values.farm_id} onChange={handleFieldChange('farm_id')}/>
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