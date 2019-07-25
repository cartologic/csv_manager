import React from 'react';
import Button from '@material-ui/core/Button';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import FormHelperText from '@material-ui/core/FormHelperText';
import CircularProgress from '@material-ui/core/CircularProgress';
import SelectForm from './SelectForm'

export default (props) => {
  const {
    publishDialogOpen, 
    handlePublishDialogClose, 
    publishDialogData,
    handlePublishDialogPublish,
    handlePublishDialogDelete,
    loading
  } = props
  const item = publishDialogData.item
  return (
    <div>
      <Dialog
        open={publishDialogOpen}
        onClose={handlePublishDialogClose}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
        fullWidth={false}
        maxWidth={'xl'}
      >
        <DialogTitle id="alert-dialog-title">{item.csv_file_name}</DialogTitle>
        <DialogContent>
          <DialogContentText id="alert-dialog-description">
            Please Decide The Following:
          </DialogContentText>
          {
            publishDialogData.error.length > 0 &&
            <FormHelperText error>{`Error: ${publishDialogData.error}`}</FormHelperText>
          }
          <SelectForm item={item} handleSelectChange={props.handleSelectChange}/>
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
