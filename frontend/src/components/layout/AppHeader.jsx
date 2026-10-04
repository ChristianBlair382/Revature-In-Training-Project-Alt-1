import { 
    AppBar, 
    Toolbar, 
    Typography, 
    Box, 
    Button,
    IconButton
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu'

export default function AppHeader({username, role, onLogout, onDrawerClick}) {
    return (
        <AppBar position='static'>
            <Toolbar sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <IconButton
                        aria-label="Open navigation drawer"
                        onClick={onDrawerClick}
                    >
                        <MenuIcon color="secondary" sx={{mr: 2}} />
                    </IconButton>
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