import React from 'react';
import Button from '@material-ui/core/Button';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import FormHelperText from '@material-ui/core/FormHelperText';
import CircularProgress from '@material-ui/core/CircularProgress';
import CloseIcon from '@material-ui/icons/Close'
import { makeStyles } from '@material-ui/core/styles';
import SelectForm from './SelectForm'

const useStyles = makeStyles(theme => ({
  dialogHeader: {
    display: 'flex',
  },
  dialogTitle: {
    flexGrow: 1
  }
}))
export default (props) => {
  const {
    publishDialogOpen,
    handlePublishDialogClose,
    publishDialogData,
    handlePublishDialogPublish,
    handlePublishDialogDelete,
    loading,
  } = props
  const { formErrors, item } = publishDialogData
  const classes = useStyles()
  return (
    <div>
      <Dialog
        open={publishDialogOpen}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
        fullWidth={false}
        maxWidth={'xl'}
      >
        <div className={classes.dialogHeader}>
          <DialogTitle id="alert-dialog-title" className={classes.dialogTitle}>{item.csv_file_name}</DialogTitle>
          <Button onClick={handlePublishDialogClose} color="primary" disabled={loading}>
            <CloseIcon />
          </Button>
        </div>
        <DialogContent>
          <DialogContentText id="alert-dialog-description">
            Please Decide The Following:
          </DialogContentText>
          {
            publishDialogData.error.length > 0 ?
            <FormHelperText error>{`Error: ${publishDialogData.error}`}</FormHelperText> :
            formErrors && formErrors.table_name && 
            <FormHelperText error>{`Error: Invalid table name! Must be Alphanumeric Ex: table_name_1, Max length: 63 character`}</FormHelperText>
            
          }
          <SelectForm formErrors={formErrors} item={item} handleSelectChange={props.handleSelectChange} />
        </DialogContent>
        <DialogActions>
          {loading && <CircularProgress size={20} />}
          <Button onClick={handlePublishDialogDelete} color="primary" disabled={loading}>
            Delete
          </Button>
          <Button onClick={handlePublishDialogPublish} color="primary" disabled={loading}>
            Publish
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  )
}
