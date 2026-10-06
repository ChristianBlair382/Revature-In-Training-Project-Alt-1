import { createTheme } from "@mui/material/styles";

const createAppTheme = (mode) => createTheme({
    palette: {
        mode,
        primary: {
            main: '#93d664'
        },
        secondary: {
            main: '#f0f298'
        },
        ...(mode === 'dark' && {
            background: {
                default: '#171c22',
                paper: '#222a32',
            },
            text: {
                primary: '#f4f7fa',
                secondary: '#c3ccd5',
            },
        }),
        ...(mode === 'light' && {
            background: {
                default: '#f7f8fa',
                paper: '#ffffff',
            },
        }),
    },
    shape: {
        borderRadius: 4
    }
});

export default createAppTheme;