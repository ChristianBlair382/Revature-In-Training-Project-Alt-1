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
    {field: 'field_job_id', headerName: "Field Job ID", width: 140, type: "number"},
    {field: 'file_url', headerName: "File URL", width: 70},
    {field: 'created_at', headerName: "Created At", width: 70},
]

export default function ServiceReportsDataGrid({onSuccess}) {
    const [service_reports, setServiceReports] = useState([]);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const [dialogOpen, setDialogOpen] = useState(false);
    const [form_values, setFormValues] = useState({
        field_job_id: '',
        file_url: '',
        notes: '',
    });

    async function fetchServiceReports() {
        setLoading(true)
        try {
            const response = await apiClient.get('/service_reports');
            setServiceReports(response.data);
            setError(null);
        } catch {
            setError('Error: Could not load service report data.');
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        fetchServiceReports();
    }, []);

    const handleFieldChange = (field) => (event) => {
        setFormValues((prev) => ({...prev, [field]: event.target.value}));
    }

    const handleCreate = async() => {
        try {
            await apiClient.post('/service_reports', {
                ...form_values,
                field_job_id: Number(form_values.field_job_id),
            });

            setDialogOpen(false);
            setFormValues({field_job_id: '', file_url: '', notes: ''});
            onSuccess(`Service Report "${form_values.file_url}" created successfully.`);
        } catch {

        }
    }

    if (loading) return <CircularProgress/>

    if (error) return <Alert severity="error">{error}</Alert>

    return (
        <Box>
            <Box>
                <DataGrid rows={service_reports} columns={columns} getRowId={(row) => row.id}/>
            </Box>
            <Button
            variant="outlined"
            sx={{mb: 2}}
            onClick={() => setDialogOpen(true)}
            >
                Add Service Report
            </Button>
            <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
                <DialogTitle>Create New Service Report</DialogTitle>
                <DialogContent>
                    <Stack spacing={2} sx={{mt: 1, minWidth: 300}}>
                        <TextField labal="Field Job ID" type="number" value={form_values.farm_id} onChange={handleFieldChange('farm_id')}/>
                        <TextField label="File URL" value={form_values.file_url} onChange={handleFieldChange('name')}/>
                        <TextField label="Notes" value={form_values.notes} onChange={handleFieldChange('notes')}/>
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