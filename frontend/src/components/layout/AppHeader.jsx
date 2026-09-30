import { AppBar, Toolbar, Typography, Box, Button } from '@mui/material';
import AgricultureIcon from '@mui/icons-material/Agriculture';

export default function AppHeader({username, role, onLogout}) {
    return (
        <AppBar position='static'>
            <Toolbar>
                <AgricultureIcon color="secondary" sx={{mr: 2}} />
                <Typography variant="6" component="h2"> 
                    AgriCore Farm Management Portal
                </Typography>
                {username && (
                    <Box>
                        <Typography>{username}({role})</Typography>
                        <Button color="inherit" onClick={onLogout}>Log Out</Button>
                    </Box>
                )}
            </Toolbar>
        </AppBar>
    )
}