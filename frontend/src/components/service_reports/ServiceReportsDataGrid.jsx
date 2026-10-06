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
    TextField,
    Tooltip,
    Typography
} from "@mui/material";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import HighlightOffIcon from "@mui/icons-material/HighlightOff";
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
    const [selectedFile, setSelectedFile] = useState(null);
    const [form_values, setFormValues] = useState({...EMPTY_FORM_VALUES});

    async function fetchServiceReports() {
        setLoading(true);
        try {
            const [reportsResponse, verificationResponse] = await Promise.all([
                apiClient.get('/service_reports'),
                apiClient.get('/service_reports/verification'),
            ]);
            const verificationById = new Map(
                verificationResponse.data.map(({service_report_id, verified}) => [service_report_id, verified])
            );
            setServiceReports(reportsResponse.data.map((report) => ({
                ...report,
                verified: verificationById.get(report.id) ?? false,
            })));
            setError(null);
        } catch {
            setError('Error: Could not load service report data or verify uploaded files.');
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
        {
            field: 'verified',
            headerName: "S3 Verified",
            width: 110,
            type: 'boolean',
            renderCell: ({value}) => (
                <Tooltip title={value ? 'File exists in S3' : 'File is missing from S3'}>
                    {value ? (
                        <CheckCircleIcon color="success" aria-label="Verified" />
                    ) : (
                        <HighlightOffIcon color="error" aria-label="Not verified" />
                    )}
                </Tooltip>
            ),
        },
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
        if (!selectedFile) {
            setActionError('Select a file to upload before creating the service report.');
            return;
        }

        setSaving(true);
        setActionError(null);
        try {
            const uploadData = new FormData();
            uploadData.append('file', selectedFile);
            const uploadResponse = await apiClient.post('/service_reports/upload', uploadData);
            const file_url = uploadResponse.data.file_url;

            await apiClient.post('/service_reports', {
                field_job_id: Number(form_values.field_job_id),
                file_url,
                notes: form_values.notes,
            });

            setDialogOpen(false);
            setFormValues({...EMPTY_FORM_VALUES});
            setSelectedFile(null);
            onSuccess(`Service Report "${selectedFile.name}" created successfully.`);
            await fetchServiceReports();
        } catch (error) {
            setActionError(error?.response?.data?.detail ?? 'Could not create service report. Check the values and try again.');
        } finally {
            setSaving(false);
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
        setSelectedFile(null);
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
                <DialogTitle>Create New Service Report</DialogTitle>
                <DialogContent>
                    <Stack spacing={2} sx={{mt: 1, minWidth: 300}}>
                        {actionError && <Alert severity="error">{actionError}</Alert>}
                        <TextField label="Field Job ID" type="number" value={form_values.field_job_id} onChange={handleFieldChange('field_job_id')}/>
                        <Button component="label" variant="outlined" disabled={saving}>
                            Choose report file
                            <input
                                hidden
                                type="file"
                                onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)}
                            />
                        </Button>
                        <Typography variant="body2">
                            {selectedFile?.name ?? 'No file selected'}
                        </Typography>
                        <TextField label="Notes" value={form_values.notes} onChange={handleFieldChange('notes')}/>
                    </Stack>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setDialogOpen(false)} disabled={saving}>Cancel</Button>
                    <Button variant="contained" onClick={handleCreate} disabled={saving || !form_values.field_job_id || !selectedFile}>
                        {saving ? 'Uploading...' : 'Create'}
                    </Button>
                </DialogActions>
            </Dialog>
            <Dialog
                open={manageDialogOpen}
                onClose={() => !saving && setManageDialogOpen(false)}
            >
                <DialogTitle>
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
                                <TextField
                                    label="Stored File URL"
                                    value={form_values.file_url}
                                    InputProps={{readOnly: true}}
                                />
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