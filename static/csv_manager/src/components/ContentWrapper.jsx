import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import Paper from '@material-ui/core/Paper';
import UploadDropZone from './UploadDropZone'
import CSVList from './CSVList'
import PublishDialog from './PublishDialog'
const useStyles = makeStyles(theme => ({
  root: {
    padding: theme.spacing(3, 2),
    minHeight: 'calc(100vh - 200px)',
  },
}));
export default (props) => {
  const classes = useStyles();
  return (
    <div>
      <Paper className={classes.root}>
        <UploadDropZone {...props} />
        <CSVList {...props} />
        <PublishDialog {...props} />
      </Paper>
    </div>
  );
}
