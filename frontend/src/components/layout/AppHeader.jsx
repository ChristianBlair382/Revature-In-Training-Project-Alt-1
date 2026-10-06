import { 
    AppBar, 
    Toolbar, 
    Typography, 
    Box, 
    Button,
    IconButton
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu'
import DarkModeIcon from '@mui/icons-material/DarkMode';
import LightModeIcon from '@mui/icons-material/LightMode';

export default function AppHeader({username, role, onLogout, onDrawerClick, mode, onToggleColorMode}) {
    return (
        <AppBar position='static' sx={{bgcolor: 'background.paper', color: 'text.primary', borderBottom: 1, borderColor: 'divider'}}>
            <Toolbar sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    {onDrawerClick && (
                        <IconButton
                            aria-label="Open navigation drawer"
                            onClick={onDrawerClick}
                        >
                            <MenuIcon color="secondary" sx={{mr: 2}} />
                        </IconButton>
                    )}
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
                <IconButton
                    aria-label={`Switch to ${mode === 'light' ? 'dark' : 'light'} mode`}
                    onClick={onToggleColorMode}
                    color="inherit"
                    sx={{ml: username ? 1 : 'auto'}}
                >
                    {mode === 'light' ? <DarkModeIcon /> : <LightModeIcon />}
                </IconButton>
            </Toolbar>
        </AppBar>
    )
}