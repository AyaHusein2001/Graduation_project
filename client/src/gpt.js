import React, { useState } from "react";
import Button from "@mui/material/Button";
import TextField from "@mui/material/TextField";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import MdDeleteForever from "@mui/icons-material/DeleteForever";
import ColorPicker from "./ColorPicker";
import axios from "axios";
import { IoMdClose } from "react-icons/io";
import { createTheme, ThemeProvider } from '@mui/material/styles';
import { green, purple } from '@mui/material/colors';
import backgroundImage from './assets/background.jpg';
import "./EntsAttrsTable.css"; // Assuming you have a CSS file for styling

const theme = createTheme({
  palette: {
    primary: {
      main: '#a819d3',
    },
    secondary: {
      main:'#ff7100',
    },
  },
});

export default function FormDialog() {
  const [openDialog, setOpenDialog] = useState(false);
  const [showColorPicker, setShowColorPicker] = useState(false);
  const [error, setError] = useState(false);
  const [databaseDescription, setDatabaseDescription] = useState("");
  const [result, setResult] = useState([]);
  const [newElement, setNewElement] = useState("");
  const [selectedColor, setSelectedColor] = useState("#ffffff");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!databaseDescription.trim()) {
      setError(true);
      return;
    }
    try {
      const response = await fetch("process-text", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text: databaseDescription }),
      });
      const data = await response.json();
      setResult(data.result);
      setOpenDialog(true);
      setError(false);
    } catch (error) {
      console.error("There was an error processing the text!", error);
      setError(true);
    }
  };

  const handleColorChange = (color) => {
    setSelectedColor(color);
  };

  const toggleColorPicker = () => {
    setShowColorPicker((prevShowColorPicker) => !prevShowColorPicker);
  };

  const divStyle = {
    backgroundImage: `url(${backgroundImage})`,
    backgroundSize: 'cover',
    backgroundRepeat: 'no-repeat',
    backgroundPosition: 'center',
    height: '100vh',
    overflow: 'hidden',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '20px', // Adjust the gap as needed
  };

  const textFieldStyle = {
    width: '50%', // Adjust the width as needed
  };

  return (
    <div className="App" style={divStyle}>
      <ThemeProvider theme={theme}>
        <React.Fragment>
          <h1 style={{ color: "#a819d3", textAlign: "center" }}>Webby</h1>
          <TextField
            id="database-description"
            label="Database Description"
            variant="standard"
            multiline
            maxRows={10}
            error={error}
            onChange={(e) => {
              setDatabaseDescription(e.target.value);
              setError(false);
            }}
            value={databaseDescription}
            sx={textFieldStyle}
          />
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <TextField
              id="gui-description"
              label="GUI Description"
              variant="standard"
              multiline
              maxRows={10}
              sx={textFieldStyle}
            />
            <Button variant="contained" color="secondary" onClick={toggleColorPicker}>
              {showColorPicker ? 'Close' : 'Open'} Color Picker
            </Button>
          </div>
          {showColorPicker && <ColorPicker onColorChange={handleColorChange} />}
          <Button variant="contained" color="primary" onClick={handleSubmit}>
            Submit
          </Button>
          <Dialog open={openDialog} onClose={() => setOpenDialog(false)}>
            <DialogTitle>Processed Results</DialogTitle>
            <DialogContent>
              {result.length > 0 ? (
                <ul>
                  {result.map((item, index) => (
                    <li key={index}>
                      {item}
                      <MdDeleteForever
                        onClick={() => setResult((prevResult) => prevResult.filter((_, i) => i !== index))}
                        style={{ cursor: "pointer", marginLeft: "10px" }}
                      />
                    </li>
                  ))}
                </ul>
              ) : (
                <DialogContentText>No results to display.</DialogContentText>
              )}
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setOpenDialog(false)} color="primary">
                Close
              </Button>
            </DialogActions>
          </Dialog>
        </React.Fragment>
      </ThemeProvider>
    </div>
  );
}
