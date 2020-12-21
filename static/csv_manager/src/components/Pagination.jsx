import React from "react";
import Button from "@material-ui/core/Button";
import ButtonGroup from "@material-ui/core/ButtonGroup";
import { makeStyles } from "@material-ui/core/styles";
import Typography from "@material-ui/core/Typography";

const useStyles = makeStyles((theme) => ({
  root: {
    display: "flex",
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    "& > *": {
      margin: theme.spacing(1),
    },
  },
}));

export default function Pagination({
  onNext,
  onPrev,
  nextUrl,
  prevUrl,
  limit,
  offset,
  total,
}) {
  const classes = useStyles();
  const min = offset;
  const max = limit + offset >= total ? total : limit + offset;
  return (
    <div className={classes.root}>
      <Typography variant="body2" display="block" gutterBottom>
        {min} - {max} of {total}
      </Typography>
      <ButtonGroup
        size="small"
        color="primary"
        aria-label="outlined primary button group"
      >
        <Button onClick={onPrev} disabled={!prevUrl}>
          Prev
        </Button>
        <Button onClick={onNext} disabled={!nextUrl}>
          Next
        </Button>
      </ButtonGroup>
    </div>
  );
}
