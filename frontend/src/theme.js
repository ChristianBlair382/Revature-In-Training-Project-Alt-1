import { createTheme } from "@mui/material";

const theme = createTheme({
    pallete: {
        mode: 'light',
        primary: {
            main: '#93d664'
        },
        secondary: {
            main: '#f0f298'
        }
    },
    shape: {
        borderRadius: 4
    }
});

export default theme;