import React, { useCallback } from 'react'
import DropZone from 'react-dropzone'
import { makeStyles } from '@material-ui/core/styles';
import Paper from '@material-ui/core/Paper';
import Typography from '@material-ui/core/Typography'
import IconButton from '@material-ui/core/IconButton'
import CloudUpload from '@material-ui/icons/CloudUpload'
const useStyles = makeStyles(theme => ({
    uploadBox: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        alignContent: 'center',
        textAlign: 'center',
        height: '150px',
    },
    dropZone: {
        width: '100%',
    },
    button: {
    },
    uploadIcon: {
        fontSize: '3.5em',
        color: '#9e9e9e'
    }
}));
export default (props) => {
    const classes = useStyles();
    const {
        onDrop,
        listLoading,
    } = props
    return (
        <Paper elevation={2} className={classes.uploadBox}>
            <DropZone className={classes.dropZone} accept={".csv"} onDrop={onDrop} disabled={listLoading}>
                <label htmlFor="icon-button-file">
                    <CloudUpload className={classes.uploadIcon} />
                </label>
                <Typography gutterBottom>
                    {"Click to upload CSV files"}
                </Typography>
            </DropZone>
        </Paper>
    )
}