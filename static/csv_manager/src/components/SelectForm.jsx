import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import Input from '@material-ui/core/Input';
import InputLabel from '@material-ui/core/InputLabel';
import MenuItem from '@material-ui/core/MenuItem';
import FormHelperText from '@material-ui/core/FormHelperText';
import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';
import TextField from '@material-ui/core/TextField';
import {WKTTYPES} from '../utils/geomtry-types'

const useStyles = makeStyles(theme => ({
  root: {
    display: 'flex',
    flexWrap: 'wrap',
  },
  formControl: {
    margin: theme.spacing(1),
    minWidth: 120,
  },
  textField: {
    marginTop: 0,
    marginBottom: 0,
  },
}));
const get_item_fields = (item) => {
  return (
    item.fields_names[0].map((field_name, i) => (<MenuItem key={i} value={field_name}>{field_name}</MenuItem>))
  )
}
const XYSelect = props => {
  const {
    classes,
    values,
    handleSelectChange,
    formErrors,
    item,
  } = props
  return (
    <React.Fragment>
      <FormControl className={classes.formControl} error={formErrors && formErrors.lon_field_name || false}>
        <InputLabel htmlFor="lon-helper">{'Lon / X'}</InputLabel>
        <Select
          value={values.lon}
          onChange={handleSelectChange}
          input={<Input name="lon_field_name" id="lon-helper" />}
        >
          <MenuItem value="">
            <em>None</em>
          </MenuItem>
          {
            item.fields_names && item.fields_names.length > 0 && get_item_fields(item)
          }
        </Select>
        <FormHelperText>Select X or Longitude Column</FormHelperText>
      </FormControl>

      <FormControl className={classes.formControl} error={formErrors && formErrors.lat_field_name || false}>
        <InputLabel htmlFor="lat-helper">{'Lat / Y'}</InputLabel>
        <Select
          value={values.lat}
          onChange={handleSelectChange}
          input={<Input name="lat_field_name" id="lat-helper" />}
        >
          <MenuItem value="">
            <em>None</em>
          </MenuItem>
          {
            item.fields_names && item.fields_names.length > 0 && get_item_fields(item)
          }
        </Select>
        <FormHelperText>Select Y or Latitude Column</FormHelperText>
      </FormControl>
    </React.Fragment>
  )
}
const WKTSelect = props => {
  const {
    classes,
    values,
    handleSelectChange,
    formErrors,
    item,
  } = props
  return (
    <React.Fragment>
      <FormControl className={classes.formControl} error={formErrors && formErrors.wkt_field_name || false}>
        <InputLabel htmlFor="lon-helper">{'Geometry Column'}</InputLabel>
        <Select
          value={values.wkt_field_name}
          onChange={handleSelectChange}
          input={<Input name="wkt_field_name" id="lon-helper" />}
        >
          <MenuItem value="">
            <em>None</em>
          </MenuItem>
          {
            item.fields_names && item.fields_names.length > 0 && get_item_fields(item)
          }
        </Select>
        <FormHelperText>Select Geometry Column / Attribute</FormHelperText>
      </FormControl>

      <FormControl className={classes.formControl} error={formErrors && formErrors.geometry_type || false}>
        <InputLabel htmlFor="lat-helper">{'Geom Type'}</InputLabel>
        <Select
          value={values.geometry_type}
          onChange={handleSelectChange}
          input={<Input name="geometry_type" id="lat-helper" />}
        >
          <MenuItem value="">
            <em>None</em>
          </MenuItem>
          {
            WKTTYPES.map((type, i) => (<MenuItem key={i} value={type}>{type}</MenuItem>))
          }
        </Select>
        <FormHelperText>Select Geometry Type</FormHelperText>
      </FormControl>
    </React.Fragment>
  )
}
export default (props) => {
  const classes = useStyles();
  const {
    item,
    handleSelectChange,
    formErrors,
    wkt,
  } = props
  const values = {
    lon: item.lon_field_name,
    lat: item.lat_field_name,
    srs: item.srs,
    table_name: item.table_name || '',
    wkt_field_name: item.wkt_field_name,
    geometry_type: item.geometry_type,
  }
  return (
    <form className={classes.root} autoComplete="off" id={'publish-select-form'}>
      <FormControl className={classes.formControl} error={formErrors && formErrors.table_name || false}>
        <TextField
          id="table-name"
          label="Name"
          className={classes.textField}
          value={values.name}
          name="table_name"
          onChange={handleSelectChange}
          margin="normal"
        />
        <FormHelperText>Enter Table Name</FormHelperText>
      </FormControl>
      {
        wkt ?
        <WKTSelect 
          classes={classes}
          values={values}
          handleSelectChange={handleSelectChange}
          formErrors={formErrors}
          item={item}
        />:
        <XYSelect 
          classes={classes}
          values={values}
          handleSelectChange={handleSelectChange}
          formErrors={formErrors}
          item={item}
        />
      }

      <FormControl className={classes.formControl}>
        <InputLabel htmlFor="srs-helper">{'SRS / Projection'}</InputLabel>
        <Select
          value={values.srs}
          onChange={handleSelectChange}
          input={<Input name="srs" id="srs-helper" />}
        >
          {/* <MenuItem value="">
            <em>None</em>
          </MenuItem> */}
          <MenuItem value={'WGS84'}>EPSG:4326 / WGS84</MenuItem>
        </Select>
        <FormHelperText>Select SRS</FormHelperText>
      </FormControl>
    </form>
  );
}
