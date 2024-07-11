// SaveComponent.jsx
import React from 'react';
import axios from 'axios';
import { Button } from '@mui/material';
const SaveComponent = ({ entitiesWithAttr, entitiesWithPks, relationships, onSave, onClose }) => {
    const handleSave = async () => {
        try {
          const relationshipsAsTuples = relationships.map(arr => ([arr[0], arr[1], arr[2], arr[3], arr[4], arr[5]]));
          await axios.post('save', {
            entitiesWithAttr,
            entitiesWithPks,
            relationships: relationshipsAsTuples
          });
          onSave();
          onClose(); // Close the dialog after saving
        } catch (error) {
          console.error("Error saving data:", error);
        }
      };

  return (
    <Button onClick={handleSave} color="primary">
    Ok
  </Button>

  );
};

export default SaveComponent;
