import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemAvatar from '@material-ui/core/ListItemAvatar';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemSecondaryAction from '@material-ui/core/ListItemSecondaryAction';
import ListItemText from '@material-ui/core/ListItemText';
import Avatar from '@material-ui/core/Avatar';
import IconButton from '@material-ui/core/IconButton';
import FormGroup from '@material-ui/core/FormGroup';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import Checkbox from '@material-ui/core/Checkbox';
import Grid from '@material-ui/core/Grid';
import CircularProgress from '@material-ui/core/CircularProgress';
import Typography from '@material-ui/core/Typography';
import Assignment from '@material-ui/icons/Assignment';
import Publish from '@material-ui/icons/Publish';
import moment from 'moment'

const useStyles = makeStyles(theme => ({
    root: {
        flexGrow: 1,
        // maxWidth: 752,
    },
    demo: {
        backgroundColor: theme.palette.background.paper,
    },
    title: {
        margin: theme.spacing(4, 0, 2),
        textAlign: 'center',
        color: '#616161',
    },
    listItemAvatar: {
        marginTop: '5px',
    },
}));
const CSVListItem = (props) => {
    let { csvItem, handlePublishDialogOpen } = props
    const classes = useStyles()
    return (
        <ListItem>
            <Grid container>
                <Grid item md={1}>
                    <ListItemAvatar className={classes.listItemAvatar}>
                        <Avatar>
                            <Assignment />
                        </Avatar>
                    </ListItemAvatar>
                </Grid>
                <Grid item md={4}>
                    <ListItemText
                        primary={csvItem.csv_file_name}
                        secondary={`Features Count: ${csvItem.features_count}`}
                    />
                </Grid>
                <Grid item md={4}>
                    <ListItemText
                        primary={<span>&#8203;</span>}
                        secondary={`Uploaded At: ${moment(new Date(csvItem.uploaded_at)).format('MMMM Do YYYY, h:mm:ss a')}`}
                    />
                </Grid>
                <Grid item md={3}>
                    <ListItemSecondaryAction>
                        <IconButton edge="end" aria-label="Delete" onClick={()=>{handlePublishDialogOpen(csvItem.id)}}>
                            <Publish />
                        </IconButton>
                    </ListItemSecondaryAction>
                </Grid>
            </Grid>
        </ListItem>
    )
}
export default (props) => {
    const classes = useStyles()
    const { 
        csvItems,
        handlePublishDialogOpen,
        uploadLoading,
    } = props
    return (
        <div className={classes.root}>
            <Grid container>
                <Grid item md={12}>
                    {uploadLoading && <CircularProgress size={20} />}
                    <Typography variant="h6" className={classes.title}>
                        CSV List
                    </Typography>
                    <div className={classes.demo}>
                        <List dense={true}>
                            {
                                csvItems.length > 0 &&
                                csvItems.map((c, i) => {
                                    return <CSVListItem csvItem={c} key={c.id} handlePublishDialogOpen={handlePublishDialogOpen}/>
                                })
                            }
                        </List>
                    </div>
                </Grid>
            </Grid>
        </div>
    );
}
