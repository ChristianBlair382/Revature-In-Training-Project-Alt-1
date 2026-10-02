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
    title: '',
    equipment_id: '',
    hand_id: '',
    status: 'Pending',
    priority: 'Medium',
};

const STATUS_VALUES = ['Pending', 'In-Progress', 'Completed', 'Failed'];
const PRIORITY_VALUES = ['Low', 'Medium', 'Critical'];

export default function FieldJobsDataGrid({onSuccess}) {
    const {user} = useAuth();
    const isAdmin = user?.role === 'Field_Operations_Admin' || user?.role === 'FOA';
    const isFieldHand = user?.role === 'Field_Hand' || user?.role === 'FH';
    const canManage = isAdmin || isFieldHand;
    const [field_jobs, setFieldJobs] = useState([]);
    const [discrepancyIds, setDiscrepancyIds] = useState(new Set());
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const [dialogOpen, setDialogOpen] = useState(false);
    const [manageDialogOpen, setManageDialogOpen] = useState(false);
    const [selectedFieldJob, setSelectedFieldJob] = useState(null);
    const [deleteConfirmation, setDeleteConfirmation] = useState(false);
    const [actionError, setActionError] = useState(null);
    const [saving, setSaving] = useState(false);
    const [form_values, setFormValues] = useState({...EMPTY_FORM_VALUES});

    async function fetchFieldJobs() {
        setLoading(true);
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

    async function fetchDiscrepancies() {
        try {
            const response = await apiClient.get('/field_jobs/discrepencies');
            setDiscrepancyIds(new Set(response.data.map((item) => item.field_job_id)));
        } catch {
            setDiscrepancyIds(new Set());
        }
    }

    useEffect(() => {
        fetchFieldJobs();
        fetchDiscrepancies();
    }, []);

    const handleFieldChange = (field) => (event) => {
        setFormValues((prev) => ({...prev, [field]: event.target.value}));
    };

    const openManageDialog = useCallback((fieldJob) => {
        setSelectedFieldJob(fieldJob);
        setFormValues({
            title: fieldJob.title,
            equipment_id: fieldJob.equipment_id,
            hand_id: fieldJob.hand_id,
            status: fieldJob.status,
            priority: fieldJob.priority,
        });
        setDeleteConfirmation(false);
        setActionError(null);
        setManageDialogOpen(true);
    }, []);

    const columns = useMemo(() => [
        {field: 'id', headerName: "ID", width: 70},
        {field: 'title', headerName: "Title", width: 210},
        {field: 'equipment_id', headerName: "Equipment ID", width: 70, type: "number"},
        {field: 'hand_id', headerName: "Hand ID", width: 70, type: "number"},
        {field: 'status', headerName: "Status", width: 90},
        {field: 'priority', headerName: "Priority", width: 90},
        {
            field: 'discrepancy',
            headerName: 'Colocation',
            width: 150,
            sortable: false,
            filterable: false,
            renderCell: ({row}) => {
                const hasDiscrepancy = discrepancyIds.has(row.id);

                return (
                    <Chip
                        label={hasDiscrepancy ? 'Discrepancy' : 'OK'}
                        color={hasDiscrepancy ? 'error' : 'success'}
                        variant={hasDiscrepancy ? 'filled' : 'outlined'}
                        size="small"
                    />
                );
            },
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
    ], [canManage, discrepancyIds, openManageDialog]);

    const handleCreate = async() => {
        setActionError(null);
        try {
            await apiClient.post('/field_jobs', {
                ...form_values,
                equipment_id: Number(form_values.equipment_id),
                hand_id: Number(form_values.hand_id),
            });

            setDialogOpen(false);
            setFormValues({...EMPTY_FORM_VALUES});
            onSuccess(`Field Job "${form_values.title}" created successfully.`);
            await fetchFieldJobs();
        } catch {
            setActionError('Could not create field job. Check the values and try again.');
        }
    };

    const handleUpdate = async() => {
        if (!selectedFieldJob) return;

        setSaving(true);
        setActionError(null);
        try {
            let updatedRow = { ...selectedFieldJob };

            if (isFieldHand) {
                if (selectedFieldJob.status !== form_values.status) {
                    const statusResponse = await apiClient.patch(`/field_jobs/${selectedFieldJob.id}/status`, {
                        status: form_values.status,
                    });
                    updatedRow = { ...updatedRow, ...statusResponse.data };
                }

                if (selectedFieldJob.priority !== form_values.priority) {
                    const priorityResponse = await apiClient.patch(`/field_jobs/${selectedFieldJob.id}/priority`, {
                        priority: form_values.priority,
                    });
                    updatedRow = { ...updatedRow, ...priorityResponse.data };
                }
            } else {
                const response = await apiClient.patch(`/field_jobs/${selectedFieldJob.id}`, {
                    ...form_values,
                    equipment_id: Number(form_values.equipment_id),
                    hand_id: Number(form_values.hand_id),
                });
                updatedRow = response.data;
            }

            setFieldJobs((currentFieldJobs) => currentFieldJobs.map((fieldJob) => (
                fieldJob.id === selectedFieldJob.id ? updatedRow : fieldJob
            )));
            setManageDialogOpen(false);
            onSuccess(`Field Job ${updatedRow.title} updated successfully.`);
        } catch {
            setActionError('Could not update field job. Check the values and try again.');
        } finally {
            setSaving(false);
        }
    };

    const handleDelete = async() => {
        if (!selectedFieldJob) return;

        setSaving(true);
        setActionError(null);
        try {
            await apiClient.delete(`/field_jobs/${selectedFieldJob.id}`);
            setFieldJobs((currentFieldJobs) => currentFieldJobs.filter((fieldJob) => fieldJob.id !== selectedFieldJob.id));
            setManageDialogOpen(false);
            onSuccess(`Field Job ${selectedFieldJob.title} deleted successfully.`);
        } catch {
            setActionError('Could not delete field job. It may still be in use.');
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
                <DataGrid rows={field_jobs} columns={columns} getRowId={(row) => row.id}/>
            </Box>
            {isAdmin && (
                <Button
                    variant="outlined"
                    sx={{mb: 2}}
                    onClick={openCreateDialog}
                >
                    Add Field Job
                </Button>
            )}
            <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
                <DialogTitle sx={{color: "black"}}>Create New Field Job</DialogTitle>
                <DialogContent>
                    <Stack spacing={2} sx={{mt: 1, minWidth: 300}}>
                        {actionError && <Alert severity="error">{actionError}</Alert>}
                        <TextField label="Title" value={form_values.title} onChange={handleFieldChange('title')}/>
                        <TextField label="Equipment ID" type="number" value={form_values.equipment_id} onChange={handleFieldChange('equipment_id')}/>
                        <TextField label="Hand ID" type="number" value={form_values.hand_id} onChange={handleFieldChange('hand_id')}/>
                        <TextField select label="Status" value={form_values.status} onChange={handleFieldChange('status')}>
                            {STATUS_VALUES.map((option) => (
                                <MenuItem key={option} value={option}>{option}</MenuItem>
                            ))}
                        </TextField>
                        <TextField select label="Priority" value={form_values.priority} onChange={handleFieldChange('priority')}>
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
            <Dialog
                open={manageDialogOpen}
                onClose={() => !saving && setManageDialogOpen(false)}
            >
                <DialogTitle sx={{color: "black"}}>
                    {deleteConfirmation ? 'Delete Field Job?' : `${isFieldHand ? 'Update' : 'Manage'} Field Job ${selectedFieldJob?.id ?? ''}`}
                </DialogTitle>
                <DialogContent>
                    <Stack spacing={2} sx={{mt: 1, minWidth: 300}}>
                        {actionError && <Alert severity="error">{actionError}</Alert>}
                        {deleteConfirmation ? (
                            <Alert severity="warning">
                                Delete {selectedFieldJob?.title}? This action cannot be undone.
                            </Alert>
                        ) : (
                            <>
                                {isFieldHand ? (
                                    <>
                                        <TextField select label="Status" value={form_values.status} onChange={handleFieldChange('status')}>
                                            {STATUS_VALUES.map((option) => (
                                                <MenuItem key={option} value={option}>{option}</MenuItem>
                                            ))}
                                        </TextField>
                                        <TextField select label="Priority" value={form_values.priority} onChange={handleFieldChange('priority')}>
                                            {PRIORITY_VALUES.map((option) => (
                                                <MenuItem key={option} value={option}>{option}</MenuItem>
                                            ))}
                                        </TextField>
                                    </>
                                ) : (
                                    <>
                                        <TextField label="Title" value={form_values.title} onChange={handleFieldChange('title')}/>
                                        <TextField label="Equipment ID" type="number" value={form_values.equipment_id} onChange={handleFieldChange('equipment_id')}/>
                                        <TextField label="Hand ID" type="number" value={form_values.hand_id} onChange={handleFieldChange('hand_id')}/>
                                        <TextField select label="Status" value={form_values.status} onChange={handleFieldChange('status')}>
                                            {STATUS_VALUES.map((option) => (
                                                <MenuItem key={option} value={option}>{option}</MenuItem>
                                            ))}
                                        </TextField>
                                        <TextField select label="Priority" value={form_values.priority} onChange={handleFieldChange('priority')}>
                                            {PRIORITY_VALUES.map((option) => (
                                                <MenuItem key={option} value={option}>{option}</MenuItem>
                                            ))}
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
                            <Button onClick={() => setDeleteConfirmation(false)} disabled={saving}>Keep Field Job</Button>
                            <Button color="error" variant="contained" onClick={handleDelete} disabled={saving}>
                                Delete Field Job
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