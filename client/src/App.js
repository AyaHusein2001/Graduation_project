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
import { createTheme, ThemeProvider } from "@mui/material/styles";
import { green, purple } from "@mui/material/colors";
import {  CssBaseline  } from '@mui/material';
import backgroundImage from "./assets/background.jpg";
import CircularProgress from "@mui/material/CircularProgress";
import { red } from '@mui/material/colors';
import headerImage from './assets/headerImage.png'; 
// const theme = createTheme({
//   palette: {
//     primary: {
//       main: "#FFFFFF",
//     },
//     secondary: {
//       main: "#ff7100",
//     },
//   },
// });
const theme = createTheme({
    palette: {
    primary: {
      main: "#FFAC35",
    },
    secondary: {
      main: "#2A3547",
    },
  },
  components: {
    MuiInput: {
      styleOverrides: {
        root: {
          '&:before': {
            borderBottomColor: '#FFAC35', // Change the underline color before focus
          },
          '&:hover:not(.Mui-disabled):before': {
            borderBottomColor: '#FFFFFF', // Change the underline color on hover
          },
          '&:after': {
            borderBottomColor: '#FFFFFF', // Change the underline color when focused
          },
        },
        input: {
          color: 'white', // Change the input text color to white
        },
      },
    },
    MuiInputLabel: {
      styleOverrides: {
        root: {
          color: '#FFAC35', // Change the label color
        },
        focused: {
          color: '#FFFFFF', // Change the label color when focused
        },
      },
    },
  },
});

export default function FormDialog() {
  const [openDialog, setOpenDialog] = useState(false);
  const [showEntsOnly, setShowEntsOnly] = useState(true);
  const [showColorPicker, setShowColorPicker] = useState(false);
  const [guiDescription, setGUIDescription] = useState('');
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
    setShowEntsOnly(false);
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
        // Only execute these lines after the first request is completed
        setOpenDialog(false); // Close the dialog after saving
        setShowEntsOnly(true);
      // Await the axios post request
      await axios.post("save", {
        entitiesWithAttr,
        entitiesWithPKs,
        relationships: relationshipsAsTuples,
      });
      

    } catch (error) {
      console.error("Error saving data:", error);
    }
  
    if (!guiDescription.trim()) {
      setError(true);
      return;
    }
    if (!selectedColor) {
      setError(true);
      return;
    }
  
    try {
      console.log(guiDescription);
      console.log(selectedColor);
  
      const response = await fetch("get-temp", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ description: guiDescription, color: selectedColor }),
      });
  
      console.log(response);
  
      setError(false);
    } catch (error) {
      console.error("There was an error processing the text!", error);
      setError(true);
    }
  };
  
  // const handleSave = async () => {
  //   try {
  //     const relationshipsAsTuples = relationships.map((arr) => [
  //       arr[0],
  //       arr[1],
  //       arr[2],
  //       arr[3],
  //       arr[4],
  //       arr[5],
  //     ]);
  //     console.log(entitiesWithAttr);
  //     console.log(entitiesWithPKs);
  //     console.log(relationshipsAsTuples);

  //     axios.post("save", {
  //       entitiesWithAttr,
  //       entitiesWithPKs,
  //       relationships: relationshipsAsTuples,
  //     });
  //     setOpenDialog(false); // Close the dialog after saving
  //     setShowEntsOnly(true);
  //   } catch (error) {
  //     console.error("Error saving data:", error);
  //   }

  //   if (!guiDescription.trim()) {
  //     setError(true);
  //     return;
  //   }
  //   if (!selectedColor) {
  //     setError(true);
  //     return;
  //   }
  //   try {
  //     console.log(guiDescription)
  //     console.log(selectedColor)

  //     const response = await fetch("get-temp", {
  //       method: "POST",
  //       headers: {
  //         "Content-Type": "application/json",
  //       },
  //       body: JSON.stringify({ description: guiDescription, color: selectedColor }),
  //     });

     
  //     console.log(response)

  //     setError(false);
  //   } catch (error) {
  //     console.error("There was an error processing the text!", error);
  //     setError(true);
  //   }
   
  // };

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
    minHeight: '100vh', // Ensure the minimum height of the viewport
    // width: '100vw',     // Ensure the full width of the viewport
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'flex-start',
    justifyContent: 'center',
    gap: '20px',        // Adjust the gap as needed
    paddingLeft: '200px',// Use camelCase for paddingLeft
    paddingBottom: '100px',// Use camelCase for paddingLeft

  };
  
  const textFieldStyle = {
    width: "50%", // Adjust the width as needed
    borderColor: error ? "red" : "black",
    
  };

  return (
    <div className="App" style={divStyle}>
      <ThemeProvider theme={theme}>
      <CssBaseline />
        <React.Fragment>
          {/* <h1 style={{ color: "#FFFFFF", textAlign: "center" }}>Webby</h1> */}

        <img src={headerImage} alt="Header" style={{ width: '20%', height: 'auto' ,marginBottom:'-80px'}}  />

   

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
            value={guiDescription}
            onChange={(e) => setGUIDescription(e.target.value)}
          />
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <Button color="primary" variant="contained" onClick={toggleColorPicker}>
              {showColorPicker ? "Close" : "Open"} Color Picker
            </Button>
          </div>
          {showColorPicker ? (
            <ColorPicker onColorChange={handleColorChange} />
          ) : (
            <></>
          )}
          <Button variant="contained" sx={{alignSelf:'center',marginLeft:'-100px'}} onClick={handleSubmit}>
            Submit
          </Button>

          <Dialog
            open={openDialog}
            onClose={handleCloseDialog}
            aria-labelledby="form-dialog-title"
          >
            <DialogTitle id="form-dialog-title">
              <h2>Customize your database</h2>
            </DialogTitle>
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
                                onMouseEnter={(e) =>
                                  (e.target.style.color = "red")
                                }
                                onMouseLeave={(e) =>
                                  (e.target.style.color = "black")
                                }
                                style={{
                                  cursor: "pointer",
                                  marginLeft: "10px",
                                }}
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
                        color="secondary"
                        variant="standard"
                        value={newElement}
                        onChange={(e) => setNewElement(e.target.value)}
                        sx={{
                          '& .MuiInput-root': {
                            '&:before': {
                              borderBottomColor: 'black', // Change the underline color before focus
                            },
                            '&:hover:not(.Mui-disabled):before': {
                              borderBottomColor: 'black', // Change the underline color on hover
                            },
                            '&:after': {
                              borderBottomColor: 'black', // Change the underline color when focused
                            },
                            '& input': {
                              color: 'black', // Change the text color to white
                            },
                          },
                          '& .MuiInputLabel-root': {
                            color: 'black', // Change the label color
                          },
                          '& .MuiInputLabel-root.Mui-focused': {
                            color: 'black', // Change the label color when focused
                          },
                        }}
                      />
                      <Button color="secondary" onClick={handleAddElement}>
                        Add
                      </Button>
                    </>
                  ) : (
                    <DialogContentText>
                      <div
                        style={{
                          display: "flex",
                          justifyContent: "center",
                          alignItems: "center",
                          height: "100px",
                        }}
                      >
                        <CircularProgress color="secondary" />
                      </div>
                    </DialogContentText>
                  )}
                </>
              ) : (
                <div>
                  {isEmptyObject(entitiesWithAttr) ? (
                    <DialogContentText>
                      <div
                        style={{
                          display: "flex",
                          justifyContent: "center",
                          alignItems: "center",
                          height: "100px",
                        }}
                      >
                        <CircularProgress color="secondary" />
                      </div>
                    </DialogContentText>
                  ) : (
                    <div>
                      <h2>Tables and Columns</h2>

                      <ul>
                        {Object.keys(entitiesWithAttr).map((entity, index) => (
                          <li key={index} style={{ padding: "10px" }}>
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
                                  sx={{
                                    '& .MuiInput-root': {
                                      '&:before': {
                                        borderBottomColor: 'black', // Change the underline color before focus
                                      },
                                      '&:hover:not(.Mui-disabled):before': {
                                        borderBottomColor: 'black', // Change the underline color on hover
                                      },
                                      '&:after': {
                                        borderBottomColor: 'black', // Change the underline color when focused
                                      },
                                      '& input': {
                                        color: 'black', // Change the text color to white
                                      },
                                    },
                                    '& .MuiInputLabel-root': {
                                      color: 'black', // Change the label color
                                    },
                                    '& .MuiInputLabel-root.Mui-focused': {
                                      color: 'black', // Change the label color when focused
                                    },
                                  }}
                                />

                              </div>
                            </div>
                          </li>
                        ))}
                      </ul>
                      {relationships.length > 0 ? (
                        <>
                          <h2>Extra Tables for Relationships</h2>
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
                        <></>
                      )}
                    </div>
                  )}
                </div>
              )}
            </DialogContent>
            <DialogActions>
              <Button color="secondary" onClick={handleCloseDialog}>
                Close
              </Button>
              {showEntsOnly ? (
                <Button  color="secondary" onClick={handleDialogSubmit}>
                  Submit
                </Button>
              ) : (
                <Button color="secondary" onClick={handleSave}>
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
