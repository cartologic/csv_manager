import React, {useState, useEffect} from 'react';
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
import Link from '@material-ui/core/Link';
import {POINTXY, WKTTYPES,} from '../utils/geomtry-types'

const uiWKTTYPES = [...WKTTYPES, 'WKT']
const useStyles = makeStyles(theme => ({
  dialogHeader: {
    display: 'flex',
  },
  dialogTitle: {
    flexGrow: 1
  },
  typesButtons:{
    display: 'flex',
    flexDirection: 'row',
  },
  typeButton:{
    margin: '1px 5px',
  },
}))
const DialogActionsArea = props => {
  const {
    loading,
    publishDialogData,
    handlePublishDialogDelete,
    handlePublishDialogPublish,
    wkt,
  } = props
  return (
    <DialogActions>
      {loading && <CircularProgress size={20} />}
      {
        publishDialogData.layerURL &&
        <Link underline={'none'} color="inherit" href={publishDialogData.layerURL}>
          <Button color="inherit">View Layer</Button>
        </Link>
      }
      <Button onClick={handlePublishDialogDelete} color="primary" disabled={loading}>
        Delete
      </Button>
      <Button onClick={()=>{handlePublishDialogPublish(wkt)}} color="primary" disabled={loading}>
        Publish
      </Button>
    </DialogActions>
  )
}
const PublishDialogData = (props) => {
  const {
    publishDialogOpen,
    handlePublishDialogClose,
    publishDialogData,
    handlePublishDialogPublish,
    handlePublishDialogDelete,
    loading,
  } = props
  const { formErrors, item } = publishDialogData
  const [wkt, setWKT] = useState('')
  const onWKTClick = wkt => {
    setWKT(wkt)
  }
  useEffect(()=>{
    if(item.geometry_type === '') setWKT('POINTXY')
    else setWKT(item.geometry_type)
  }, [item.geometry_type])
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
          <div className={classes.typesButton}>
            <Button className={classes.typeButton} variant={wkt === POINTXY ? 'contained' : 'text'} onClick={()=>{onWKTClick('POINTXY')}} color="primary">
              XY
            </Button>
            <Button className={classes.typeButton} variant={uiWKTTYPES.indexOf(wkt) !== -1 ? 'contained' : 'text'} onClick={()=>{onWKTClick('WKT')}} color="primary">
              WKT
            </Button>
          </div>
        </DialogContent>
        <DialogContent>
          {
            publishDialogData.error.length > 0 ?
              <FormHelperText error>{`Error: ${publishDialogData.error}`}</FormHelperText> :
              formErrors && formErrors.table_name &&
              <FormHelperText error>{`Error: Invalid table name! Must be Alphanumeric Ex: table_name_1, Max length: 63 character`}</FormHelperText>

          }
          <SelectForm formErrors={formErrors} item={item} handleSelectChange={props.handleSelectChange} wkt={wkt !== POINTXY} />
        </DialogContent>
        <DialogActionsArea
          loading={loading}
          publishDialogData={publishDialogData}
          handlePublishDialogDelete={handlePublishDialogDelete}
          handlePublishDialogPublish={handlePublishDialogPublish}
          wkt={wkt !== POINTXY}
         />
      </Dialog>
    </div>
  )
}

export default PublishDialogData;