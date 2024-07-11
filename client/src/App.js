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
import "./EntsAttrsTable.css"; // Assuming you have a CSS file for styling
import { createTheme,ThemeProvider } from '@mui/material/styles';
import { green, purple } from '@mui/material/colors';
import backgroundImage from './assets/background.jpg';
import CircularProgress from '@mui/material/CircularProgress';

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
  const [showEntsOnly, setShowEntsOnly] = useState(true);
  const [showColorPicker, setShowColorPicker] = useState(false);

  const [databaseDescription, setDatabaseDescription] = useState("");
  const [result, setResult] = useState([]);
  const [error, setError] = useState(false);
  const [newElement, setNewElement] = useState("");
  const [hideDeleteIcons, setHideDeleteIcons] = useState(false);
  const [entitiesWithAttr, setEntitiesWithAttr] = useState([]);
  const [entitiesWithPKs, setEntitiesWithPKs] = useState([]);
  const [relationships, setRelationships] = useState([]);
  const [selectedColor, setSelectedColor] = useState("#ffffff");
  const handleDelete = (entity, attr) => {
    setEntitiesWithAttr((prevEntities) => ({
      ...prevEntities,
      [entity]: prevEntities[entity].filter((attribute) => attribute !== attr),
    }));
  };

  const handleAdd = (entity, newAttr) => {
    if (newAttr) {
      setEntitiesWithAttr((prevEntities) => ({
        ...prevEntities,
        [entity]: [...prevEntities[entity], newAttr],
      }));
    }
  };

  const isEmptyObject = (obj) => Object.keys(obj).length === 0;

  const isPrimaryKey = (entity, attr) => {
    return entitiesWithPKs[entity] === attr;
  };

  const isForeignKey = (entity, attr) => {
    return relationships.some(
      (rel) =>
        (rel[1] === entity &&
          rel[2] === "many" &&
          rel[3] === "1" &&
          rel[4] === attr) ||
        (rel[1] === "1" && rel[3] === entity && rel[4] === attr)
    );
  };

  const handleSubmit = async (e) => {
    setOpenDialog(true);
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
      
      setError(false);
    } catch (error) {
      console.error("There was an error processing the text!", error);
      setError(true);
    }
  };

  const handleAddElement = () => {
    if (newElement.trim()) {
      const updatedResult = [...result, newElement];
      setResult(updatedResult);
      setNewElement("");
    }
  };

  const handleDeleteElement = (index) => {
    const updatedResult = result.filter((_, i) => i !== index);
    setResult(updatedResult);
  };

  const handleDialogSubmit = async (e) => {
    e.preventDefault();

    if (!databaseDescription.trim()) {
      setError(true);
      return;
    }

    try {
      const response = await fetch("process-data", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          description: databaseDescription,
          entities: result,
        }),
      });

      const data = await response.json();
      console.log(data);
      setEntitiesWithAttr(data.entities_with_attr);
      setEntitiesWithPKs(data.entities_with_pks);
      setRelationships(data.relationships);
      setResult([]); // Clear the result state
      setShowEntsOnly(false);
    } catch (error) {
      console.error("There was an error processing the data!", error);
    }
  };

  const handleSave = async () => {
    try {
      const relationshipsAsTuples = relationships.map((arr) => [
        arr[0],
        arr[1],
        arr[2],
        arr[3],
        arr[4],
        arr[5],
      ]);
      console.log(entitiesWithAttr);
      console.log(entitiesWithPKs);
      console.log(relationshipsAsTuples);

      axios.post("save", {
        entitiesWithAttr,
        entitiesWithPKs,
        relationships: relationshipsAsTuples,
      });
      setOpenDialog(false); // Close the dialog after saving
      setShowEntsOnly(true);
    } catch (error) {
      console.error("Error saving data:", error);
    }
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setShowEntsOnly(true);

    setResult([]);
    setNewElement("");
    setHideDeleteIcons(false);
  };

  const handleColorChange = (color) => {
    setSelectedColor(color);
    console.log("Selected color in App:", color);
    // You can perform further actions with the selected color here
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
    // overflow: 'hidden',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '20px', // Adjust the gap as needed
  };

  const textFieldStyle = {
    width: '50%', // Adjust the width as needed
    borderColor: error ? "red" : "" 
  };


  return (
    <div className="App" style={divStyle}>
    <ThemeProvider theme={theme}>
    <React.Fragment>
      <h1 style={{ color: "#a819d3", textAlign: "center" }}>Webby</h1>

      <TextField
        id="standard-basic-2"
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

      <TextField
        id="standard-basic-1"
        label="GUI Description"
        variant="standard"
        fullWidth
        multiline
        maxRows={10}
        sx={textFieldStyle}
      />
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>

        
        <Button  color="primary" onClick={toggleColorPicker}>
              {showColorPicker ? 'Close' : 'Open'} Color Picker
            </Button>
            
      </div>
      {showColorPicker ? <ColorPicker onColorChange={handleColorChange} />:<></>}
      <Button variant="contained" onClick={handleSubmit}>
        Submit
      </Button>

      <Dialog
        open={openDialog}
        onClose={handleCloseDialog}
        aria-labelledby="form-dialog-title"
      >
        <DialogTitle id="form-dialog-title"><h2>Customize your database</h2></DialogTitle>
        <DialogContent>
          {showEntsOnly ? (
            <>
              {result.length > 0 ? (
                <>
                <h2>Tabels names</h2>
                <ul>
                  {result.map((item, index) => (
                    <li key={index}>
                      {item}
                      {!hideDeleteIcons && (
                        <MdDeleteForever
                          onClick={() => handleDeleteElement(index)}
                          onMouseEnter={(e) => (e.target.style.color = "red")}
                          onMouseLeave={(e) => (e.target.style.color = "black")}
                          style={{ cursor: "pointer", marginLeft: "10px" }}
                        />
                      )}
                    </li>
                  ))}
                </ul>
                <TextField
                margin="dense"
                id="newElement"
                label="New Table"
                fullWidth
                variant="standard"
                value={newElement}
                onChange={(e) => setNewElement(e.target.value)}
              />
              <Button onClick={handleAddElement} color="primary">
                Add
              </Button>
                </>
              ) : (
                <DialogContentText>
                <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100px' }}>
                  <CircularProgress color="primary" />
                </div>
              </DialogContentText>
              )}
              
            </>
          ) : (
            <div>
              
              {isEmptyObject(entitiesWithAttr) ? (
                <p>No entities with attributes found</p>
              ) : (
                <div>
                  <h2>Tables and Columns</h2>
                  {isEmptyObject(entitiesWithAttr) ? (
                    <p>No entities with attributes found</p>
                  ) : (
                    <ul>
                      {Object.keys(entitiesWithAttr).map((entity, index) => (
                        <li key={index} style={{ padding: '10px' }}>
                          <div>
                            <strong>{entity}</strong>:
                            <div className="attributes-row">
                              {entitiesWithAttr[entity].map(
                                (attr, attrIndex) => (
                                  <div
                                    className={`attribute ${
                                      isPrimaryKey(entity, attr)
                                        ? "primary-key"
                                        : ""
                                    } ${
                                      isForeignKey(entity, attr)
                                        ? "foreign-key"
                                        : ""
                                    }`}
                                    key={attrIndex}
                                  >
                                    {attr}{" "}
                                    {isPrimaryKey(entity, attr) ? "(pk)" : ""}{" "}
                                    {isForeignKey(entity, attr) ? "(fk)" : ""}
                                    {!isPrimaryKey(entity, attr) &&
                                      !isForeignKey(entity, attr) && (
                                        <IoMdClose
                                          className="close-icon"
                                          onClick={() =>
                                            handleDelete(entity, attr)
                                          }
                                        />
                                      )}
                                  </div>
                                )
                              )}
                            </div>
                            <div className="add-attribute">
                              <TextField
                                type="text"
                                label="New Column"
                                variant="standard"
                                onKeyDown={(e) => {
                                  if (e.key === "Enter") {
                                    handleAdd(entity, e.target.value);
                                    e.target.value = "";
                                  }
                                }}
                              />
                              <Button
                                onClick={(e) => {
                                  const input = e.target.previousSibling;
                                  handleAdd(entity, input.value);
                                  input.value = "";
                                }}
                              >
                                Add
                              </Button>
                            </div>
                          </div>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              )}

              <h2>Extra Tables for Relationships</h2>
              {relationships.length > 0 ? (
                <>
                  <ul>
                    {relationships.map((relationship, index) =>
                      relationship[0] === "many" &&
                      relationship[2] === "many" ? (
                        <li key={index}>
                          {relationship[1]}_{relationship[3]}
                        </li>
                      ) : null
                    )}
                  </ul>
                </>
              ) : (
                <p>No results to display.</p>
              )}
            </div>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog} color="primary">
            Close
          </Button>
          {showEntsOnly ? (
            <Button onClick={handleDialogSubmit} color="primary">
              Submit
            </Button>
          ) : (
            <Button onClick={handleSave} color="primary">
              Ok
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </React.Fragment>
    </ThemeProvider>
    </div>
  );
}
