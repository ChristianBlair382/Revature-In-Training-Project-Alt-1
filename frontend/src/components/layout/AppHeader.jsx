import { AppBar, Toolbar, Typography, Box, Button } from '@mui/material';
import AgricultureIcon from '@mui/icons-material/Agriculture';

export default function AppHeader({username, role, onLogout}) {
    return (
        <AppBar position='static'>
            <Toolbar sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <AgricultureIcon color="secondary" sx={{mr: 2}} />
                    <Typography variant="h6" component="h2">
                        AgriCore Farm Management Portal
                    </Typography>
                </Box>
                {username && (
                    <Box sx={{ display: 'flex', alignItems: 'center', ml: 'auto' }}>
                        <Typography sx={{ mr: 2 }}>{username} ({role})</Typography>
                        <Button color="inherit" onClick={onLogout}>Log Out</Button>
                    </Box>
                )}
            </Toolbar>
        </AppBar>
    )
}