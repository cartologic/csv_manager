import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import Input from '@material-ui/core/Input';
import InputLabel from '@material-ui/core/InputLabel';
import MenuItem from '@material-ui/core/MenuItem';
import FormHelperText from '@material-ui/core/FormHelperText';
import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';
import TextField from '@material-ui/core/TextField';

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
export default (props) => {
  const classes = useStyles();
  const {
    item,
    handleSelectChange,
    formErrors
  } = props
  const values = {
    lon: item.lon_field_name,
    lat: item.lat_field_name,
    srs: item.srs,
    table_name: item.table_name || ''
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
        <FormHelperText>Please Enter Table Name</FormHelperText>
      </FormControl>
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
        <FormHelperText>Please Select X or Longitude Column</FormHelperText>
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
        <FormHelperText>Please Select Y or Latitude Column</FormHelperText>
      </FormControl>

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
        <FormHelperText>Please Select SRS</FormHelperText>
      </FormControl>
    </form>
  );
}
