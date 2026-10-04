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
    TextField
} from "@mui/material";
import apiClient from "../../api/client.js";
import { useAuth } from "../../context/AuthContext.jsx";

const EMPTY_FORM_VALUES = {
    field_job_id: '',
    file_url: '',
    notes: '',
};

export default function ServiceReportsDataGrid({onSuccess}) {
    const {user} = useAuth();
    const isAdmin = user?.role === 'Field_Operations_Admin' || user?.role === 'FOA';
    const [service_reports, setServiceReports] = useState([]);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const [dialogOpen, setDialogOpen] = useState(false);
    const [manageDialogOpen, setManageDialogOpen] = useState(false);
    const [selectedServiceReport, setSelectedServiceReport] = useState(null);
    const [deleteConfirmation, setDeleteConfirmation] = useState(false);
    const [actionError, setActionError] = useState(null);
    const [saving, setSaving] = useState(false);
    const [form_values, setFormValues] = useState({...EMPTY_FORM_VALUES});

    async function fetchServiceReports() {
        setLoading(true);
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
    };

    const openManageDialog = useCallback((serviceReport) => {
        setSelectedServiceReport(serviceReport);
        setFormValues({
            field_job_id: serviceReport.field_job_id,
            file_url: serviceReport.file_url,
            notes: serviceReport.notes ?? '',
        });
        setDeleteConfirmation(false);
        setActionError(null);
        setManageDialogOpen(true);
    }, []);

    const columns = useMemo(() => [
        {field: 'id', headerName: "ID", width: 70},
        {field: 'field_job_id', headerName: "Field Job ID", width: 140, type: "number"},
        {field: 'file_url', headerName: "File URL", width: 230},
        {field: 'notes', headerName: "Notes", width: 200},
        {field: 'created_at', headerName: "Created At", width: 180},
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
    ], [isAdmin, openManageDialog]);

    const handleCreate = async() => {
        setActionError(null);
        try {
            await apiClient.post('/service_reports', {
                ...form_values,
                field_job_id: Number(form_values.field_job_id),
            });

            setDialogOpen(false);
            setFormValues({...EMPTY_FORM_VALUES});
            onSuccess(`Service Report "${form_values.file_url}" created successfully.`);
            await fetchServiceReports();
        } catch {
            setActionError('Could not create service report. Check the values and try again.');
        }
    };

    const handleUpdate = async() => {
        if (!selectedServiceReport) return;

        setSaving(true);
        setActionError(null);
        try {
            const response = await apiClient.patch(`/service_reports/${selectedServiceReport.id}`, {
                ...form_values,
                field_job_id: Number(form_values.field_job_id),
            });
            setServiceReports((currentServiceReports) => currentServiceReports.map((serviceReport) => (
                serviceReport.id === selectedServiceReport.id ? response.data : serviceReport
            )));
            setManageDialogOpen(false);
            onSuccess(`Service Report ${response.data.id} updated successfully.`);
        } catch {
            setActionError('Could not update service report. Check the values and try again.');
        } finally {
            setSaving(false);
        }
    };

    const handleDelete = async() => {
        if (!selectedServiceReport) return;

        setSaving(true);
        setActionError(null);
        try {
            await apiClient.delete(`/service_reports/${selectedServiceReport.id}`);
            setServiceReports((currentServiceReports) => currentServiceReports.filter((serviceReport) => serviceReport.id !== selectedServiceReport.id));
            setManageDialogOpen(false);
            onSuccess(`Service Report ${selectedServiceReport.id} deleted successfully.`);
        } catch {
            setActionError('Could not delete service report. It may still be in use.');
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
                    rows={service_reports} 
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
                    Add Service Report
                </Button>
            )}
            <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
                <DialogTitle sx={{color: "black"}}>Create New Service Report</DialogTitle>
                <DialogContent>
                    <Stack spacing={2} sx={{mt: 1, minWidth: 300}}>
                        {actionError && <Alert severity="error">{actionError}</Alert>}
                        <TextField label="Field Job ID" type="number" value={form_values.field_job_id} onChange={handleFieldChange('field_job_id')}/>
                        <TextField label="File URL" value={form_values.file_url} onChange={handleFieldChange('file_url')}/>
                        <TextField label="Notes" value={form_values.notes} onChange={handleFieldChange('notes')}/>
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
                    {deleteConfirmation ? 'Delete Service Report?' : `Manage Service Report ${selectedServiceReport?.id ?? ''}`}
                </DialogTitle>
                <DialogContent>
                    <Stack spacing={2} sx={{mt: 1, minWidth: 300}}>
                        {actionError && <Alert severity="error">{actionError}</Alert>}
                        {deleteConfirmation ? (
                            <Alert severity="warning">
                                Delete Service Report {selectedServiceReport?.id}? This action cannot be undone.
                            </Alert>
                        ) : (
                            <>
                                <TextField label="Field Job ID" type="number" value={form_values.field_job_id} onChange={handleFieldChange('field_job_id')}/>
                                <TextField label="File URL" value={form_values.file_url} onChange={handleFieldChange('file_url')}/>
                                <TextField label="Notes" value={form_values.notes} onChange={handleFieldChange('notes')}/>
                            </>
                        )}
                    </Stack>
                </DialogContent>
                <DialogActions>
                    {deleteConfirmation ? (
                        <>
                            <Button onClick={() => setDeleteConfirmation(false)} disabled={saving}>Keep Service Report</Button>
                            <Button color="error" variant="contained" onClick={handleDelete} disabled={saving}>
                                Delete Service Report
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