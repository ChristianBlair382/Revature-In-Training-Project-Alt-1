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
    {field: 'title', headerName: "Title", width: 210},
    {field: 'equipment_id', headerName: "Equipment ID", width: 70, type: "number"},
    {field: 'hand_id', headerName: "Hand ID", width: 70, type: "number"},
    {field: 'status', headerName: "Status", width: 70},
    {field: 'priority', headerName: "Priority", width: 70},
]

const STATUS_VALUES = ['Pending', 'In-Progress', 'Completed', 'Failed']
const PRIORITY_VALUES = ['Low', 'Medium', 'Critical']

export default function FieldJobsDataGrid({onSuccess}) {
    const [field_jobs, setFieldJobs] = useState([]);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const [dialogOpen, setDialogOpen] = useState(false);
    const [form_values, setFormValues] = useState({
        title: '',
        equipment_id: '',
        hand_id: '',
        status: 'Idle',
        priority: 'Medium',
    });

    async function fetchFieldJobs() {
        setLoading(true)
        try {
            const response = await apiClient.get('/field_jobs');
            setFieldJobs(response.data);
            setError(null);
        } catch {
            setError('Error: Could not load field job data.');
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        fetchFieldJobs();
    }, []);

    const handleFieldChange = (field) => (event) => {
        setFormValues((prev) => ({...prev, [field]: event.target.value}));
    }

    const handleCreate = async() => {
        try {
            await apiClient.post('/field_jobs', {
                ...form_values,
                equipment_id: Number(form_values.equipment_id),
                hand_id: Number(form_values.hand_id),
            });

            setDialogOpen(false);
            setFormValues({title: '', equipment_id: '', hand_id: '', status: 'Idle', priority: 'Medium',});
            onSuccess(`Field Job "${form_values.title}" created successfully.`);
        } catch {

        }
    }

    if (loading) return <CircularProgress/>

    if (error) return <Alert severity="error">{error}</Alert>

    return (
        <Box>
            <Box>
                <DataGrid rows={field_jobs} columns={columns} getRowId={(row) => row.id}/>
            </Box>
            <Button
            variant="outlined"
            sx={{mb: 2}}
            onClick={() => setDialogOpen(true)}
            >
                Add Field Job
            </Button>
            <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
                <DialogTitle>Create New Field Job</DialogTitle>
                <DialogContent>
                    <Stack spacing={2} sx={{mt: 1, minWidth: 300}}>
                        <TextField label="Title" value={form_values.title} onChange={handleFieldChange('title')}/>
                        <TextField label="Equipment ID" type="number" value={form_values.equipment_id} onChange={handleFieldChange('equipment_id')}/>
                        <TextField label="Hand ID" type="number" value={form_values.hand_id} onChange={handleFieldChange('hand_id')}/>
                        <TextField select label="Status" onChange={handleFieldChange('status')}>
                            {STATUS_VALUES.map((option) => (
                                <MenuItem key={option} value={option}>{option}</MenuItem>
                            ))}
                        </TextField>
                        <TextField select label="Priority" onChange={handleFieldChange('priority')}>
                            {PRIORITY_VALUES.map((option) => (
                                <MenuItem key={option} value={option}>{option}</MenuItem>
                            ))}
                        </TextField>
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