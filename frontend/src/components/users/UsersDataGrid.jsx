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
    {field: 'username', headerName: "Username", width: 140},
    {field: 'role', headerName: "Role", width: 210},
]

const ROLE_VALUES = ['Field_Operations_Admin', 'Field_Hand', 'Auditor'];

export default function UsersDataGrid({onSuccess}) {
    const [users, setUsers] = useState([]);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const [dialogOpen, setDialogOpen] = useState(false);
    const [form_values, setFormValues] = useState({
        username: '',
        password: '',
        role: 'Auditor',
    });

    async function fetchUsers() {
        setLoading(true)
        try {
            const response = await apiClient.get('/users');
            setUsers(response.data);
            setError(null);
        } catch {
            setError('Error: Could not load user data.');
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        fetchUsers();
    }, []);

    const handleFieldChange = (field) => (event) => {
        setFormValues((prev) => ({...prev, [field]: event.target.value}));
    }

    const handleCreate = async() => {
        try {
            await apiClient.post('/users', {
                ...form_values,
            });

            setDialogOpen(false);
            setFormValues({username: '', password: '', role: 'Auditor',});
            onSuccess(`User "${form_values.username}" added successfully.`);
        } catch {

        }
    }

    if (loading) return <CircularProgress/>

    if (error) return <Alert severity="error">{error}</Alert>

    return (
        <Box>
            <Box>
                <DataGrid rows={users} columns={columns} getRowId={(row) => row.id}/>
            </Box>
            <Button
            variant="outlined"
            sx={{mb: 2}}
            onClick={() => setDialogOpen(true)}
            >
                Add User
            </Button>
            <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
                <DialogTitle>Create New User</DialogTitle>
                <DialogContent>
                    <Stack spacing={2} sx={{mt: 1, minWidth: 300}}>
                        <TextField label="Username" value={form_values.username} onChange={handleFieldChange('username')}/>
                        <TextField label="Password" value={form_values.password} onChange={handleFieldChange('password')}/>
                        <TextField select label="Role" value={form_values.role} onChange={handleFieldChange('role')}>
                            {ROLE_VALUES.map((option) => (
                                <MenuItem key={option} value={option}>{option}</MenuItem>
                            ))}
                        </TextField>
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