import React, { useEffect } from "react"
import { Button, Card, CardContent, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle } from "@material-ui/core"
import { useDispatch, useSelector } from "react-redux";
import { clearMessage } from "../slices/messageSlice";

export default function NotificationBox() {
  const [open, setOpen] = React.useState(false);
  const dispatch = useDispatch();
  const { message } = useSelector((state) => state.message);

  const handleClose = () => {
    dispatch(clearMessage());
    setOpen(false);
  }

  useEffect(() => {
    if (!message === "") {
      setOpen(true);
    }
  }, [message])

  return (
    <Dialog open={open} >
      <Card >
        <CardContent>
          <DialogTitle>Alert</DialogTitle>
          <DialogContent>
            <DialogContentText>
              {message}
            </DialogContentText>
          </DialogContent>
          <DialogActions>
            <Button
              id="cancel-removedb"
              onClick={handleClose}
              variant="outlined"
              color="primary"
            >Ok</Button>
          </DialogActions>
        </CardContent>
      </Card>
    </Dialog>
  )
}