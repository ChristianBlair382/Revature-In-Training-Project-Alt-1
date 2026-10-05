import { useState } from "react";
import { Box, Paper, Alert, Button, Typography, TextField } from "@mui/material";
import { useAuth } from "../../context/AuthContext.jsx";
import AgricultureIcon from "@mui/icons-material/Agriculture";

export default function LoginForm() {
    const {login} = useAuth();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = async (event) => {
        event.preventDefault()
        setError(null);
        try {
            await login(username, password);
        } catch (err) {
            if(err.response?.status === 401) {
                setError('Username or Password is incorrect.');
            } else {
                setError('Something went wrong! Please try again later.');
            }
        }
    }

    return (
        <Box sx={{display: 'flex', justifyContent: 'center', mt: 8}}>
            <Paper
                component="form"
                onSubmit={handleSubmit}
                variant="outlined"
                sx={{p: 4, width: 320}}
            >
                <Box sx={{display: "flex", alignItems: "center"}}>
                    <AgricultureIcon color="primary" sx={{fontSize: 80}} />
                    <Typography
                        variant="h4"
                        gutterBottom
                    >
                        AgriCore
                    </Typography>
                </Box>
                
                { error &&
                    <Alert severity="error" sx={{ mb: 2 }}>
                        {error}
                    </Alert>
                }
                <TextField 
                    label="Username"
                    fullWidth
                    margin="normal"
                    value={username}
                    onChange={(event) => setUsername(event.target.value)}
                />
                <TextField 
                    label="Password"
                    type="password"
                    fullWidth
                    margin="normal"
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                />
                <Button
                    type="submit"
                    variant="contained"
                    fullWidth
                    sx={{ mb: 2 }}
                >
                    Log In
                </Button>
            </Paper>
        </Box>
    )
}